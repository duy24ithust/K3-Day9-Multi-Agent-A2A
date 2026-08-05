import os
import sys
import json
from pathlib import Path
from typing import Optional, List

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import BaseModel

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_openrouter import ChatOpenRouter
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

from src.contracts import OrderSellerResult, PaymentResult, PolicyResult, ResponsibleParty
from src.tools.delivery_tools import analyze_delivery_with_pandas, DeliveryCheckResult, DeliveryAssessment


class DeliveryAgent:
    """
    Delivery & Policy Agent (Member 4) using OpenRouter LLM (nvidia/nemotron-nano-9b-v2:free),
    Pandas delivery tool, and returning Pydantic PolicyResult contracts for CoordinatorAgent integration.
    """
    def __init__(self, model_name: str = "nvidia/nemotron-nano-9b-v2:free", data_dir: str = "data"):
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

        if HAS_LANGCHAIN and api_key:
            try:
                self.llm = ChatOpenRouter(
                    model=model_name,
                    openrouter_api_key=api_key,
                    temperature=0.0
                )
            except Exception:
                self.llm = None
        else:
            self.llm = None
        self.data_dir = data_dir

    def analyze_delivery_check(self, order_id: str) -> DeliveryCheckResult:
        """
        Directly invoke the Pandas delivery tool returning concise DeliveryCheckResult Pydantic model.
        """
        return analyze_delivery_with_pandas(order_id, self.data_dir)

    def evaluate(self, order_seller_res: OrderSellerResult, payment_res: PaymentResult, customer_message: str = "") -> PolicyResult:
        """
        Evaluate dispute rules given OrderSellerResult and PaymentResult, returning PolicyResult.
        Matches the contract expected by CoordinatorAgent.
        """
        order_id = order_seller_res.order_id

        # 1. Run Pandas tool for ground-truth delivery check
        delivery_check: DeliveryCheckResult = self.analyze_delivery_check(order_id)
        assessment: DeliveryAssessment = delivery_check.delivery_assessment

        # 2. Priority Rule Engine Evaluation based on EC_POLICY_V1 (Mục 4 README)
        order_status = order_seller_res.order_status if order_seller_res.order_status != "unknown" else "delivered"

        primary_issue = "unsupported_late_claim"
        root_cause_code = "DELIVERY_WITHIN_ESTIMATE"
        responsible_parties: List[ResponsibleParty] = []
        recommended_refund_brl = 0.0
        resolution_actions: List[str] = ["reject_late_refund"]
        case_status = "no_action"

        if order_status == "canceled" and payment_res.payment_total_brl > 0:
            primary_issue = "canceled_order_paid"
            root_cause_code = "ORDER_CANCELED_AFTER_PAYMENT"
            responsible_parties = [ResponsibleParty(party_type="platform", party_id="OLIST_PLATFORM")]
            recommended_refund_brl = payment_res.payment_total_brl
            resolution_actions = ["issue_full_refund"]
            case_status = "action_required"

        elif order_status == "unavailable" and payment_res.payment_total_brl > 0:
            primary_issue = "unavailable_order_paid"
            root_cause_code = "ORDER_UNAVAILABLE_AFTER_PAYMENT"
            responsible_parties = [ResponsibleParty(party_type="platform", party_id="OLIST_PLATFORM")]
            recommended_refund_brl = payment_res.payment_total_brl
            resolution_actions = ["issue_full_refund"]
            case_status = "action_required"

        elif assessment.is_delivered_late and assessment.seller_handoff_late:
            primary_issue = "late_delivery_seller"
            root_cause_code = "SELLER_HANDOFF_AFTER_LIMIT"
            seller_id = order_seller_res.seller_ids[0] if order_seller_res.seller_ids else (
                assessment.responsible_party.party_id if assessment.responsible_party else "UNKNOWN_SELLER"
            )
            responsible_parties = [ResponsibleParty(party_type="seller", party_id=seller_id)]
            recommended_refund_brl = order_seller_res.freight_total_brl
            resolution_actions = ["refund_freight"]
            case_status = "action_required"

        elif assessment.is_delivered_late and not assessment.seller_handoff_late:
            primary_issue = "late_delivery_logistics"
            root_cause_code = "CARRIER_DELIVERED_AFTER_ESTIMATE"
            responsible_parties = [ResponsibleParty(party_type="logistics_provider", party_id="LOGISTICS_PROVIDER")]
            recommended_refund_brl = order_seller_res.freight_total_brl
            resolution_actions = ["refund_freight"]
            case_status = "action_required"

        elif payment_res.is_split_payment and payment_res.payment_matches_order_total:
            primary_issue = "valid_split_payment"
            root_cause_code = "MULTIPLE_PAYMENTS_RECONCILED"
            responsible_parties = []
            recommended_refund_brl = 0.0
            resolution_actions = ["explain_valid_split_payment"]
            case_status = "no_action"

        else:
            primary_issue = "unsupported_late_claim"
            root_cause_code = "DELIVERY_WITHIN_ESTIMATE"
            responsible_parties = []
            recommended_refund_brl = 0.0
            resolution_actions = ["reject_late_refund"]
            case_status = "no_action"

        policy_evidence_id = f"policy:{root_cause_code}"

        # 3. Enhance / Validate with OpenAI gpt-4o-mini LLM reasoning if available
        confidence = 1.0

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                system_prompt = (
                    "You are an expert E-commerce Policy & Dispute Agent. "
                    "Analyze the customer claim against determined policy issue and output JSON with confidence (0.0 to 1.0)."
                )
                user_msg = (
                    f"Customer Message: {customer_message}\n"
                    f"Determined Issue: {primary_issue}\n"
                    f"Root Cause: {root_cause_code}\n"
                    f"Refund: {recommended_refund_brl} BRL"
                )
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0
                )
                res_data = json.loads(resp.choices[0].message.content)
                if "confidence" in res_data:
                    c_val = float(res_data["confidence"])
                    if 0.0 <= c_val <= 1.0:
                        confidence = round(c_val, 2)
            except Exception:
                pass

        return PolicyResult(
            primary_issue=primary_issue,
            case_status=case_status,
            confidence=confidence,
            root_cause_code=root_cause_code,
            responsible_parties=responsible_parties,
            recommended_refund_brl=round(recommended_refund_brl, 2),
            resolution_actions=resolution_actions,
            policy_evidence_id=policy_evidence_id
        )

if __name__ == "__main__":
    # Smoke test for DeliveryAgent
    agent = DeliveryAgent()
    check_result = agent.analyze_delivery_check("e481f51cbdc54678b7cc49136f2d6af7")
    print("DeliveryCheckResult Pydantic output:")
    print(check_result.model_dump_json(indent=2))
