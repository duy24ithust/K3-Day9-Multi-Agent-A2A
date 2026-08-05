"""
Policy Agent & Delivery Agent module for multi-agent e-commerce dispute resolution.
Implements the business logic rules of EC_POLICY_V1 in strict priority order,
with LLM support (<=10B model declared in code, API key loaded from .env).
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from src.contracts import OrderSellerResult, PaymentResult, PolicyResult, ResponsibleParty

# Model declared in code as required by rule 4 (<= 10B parameters)
LLM_MODEL_NAME = "meta-llama/llama-3.1-8b-instruct:free"

load_dotenv()


class PolicyAgent:
    """Agent responsible for evaluating business rules (EC_POLICY_V1) and determining resolution."""

    def __init__(self):
        self.model_name = LLM_MODEL_NAME
        self.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    def _call_llm_reasoning(self, order_seller_res: OrderSellerResult, payment_res: PaymentResult) -> Optional[str]:
        """Calls LLM provider if API key is provided in .env."""
        if not self.api_key or self.api_key.startswith("sk-or-xxx"):
            return None

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            prompt = (
                f"Evaluate case for order {order_seller_res.order_id}:\n"
                f"- Order Status: {order_seller_res.order_status}\n"
                f"- Carrier Date: {order_seller_res.delivered_carrier_date}\n"
                f"- Customer Delivery Date: {order_seller_res.delivered_customer_date}\n"
                f"- Estimated Delivery Date: {order_seller_res.estimated_delivery_date}\n"
                f"- Late Seller IDs: {order_seller_res.late_seller_ids}\n"
                f"- Item Total: {order_seller_res.item_total_brl}\n"
                f"- Freight Total: {order_seller_res.freight_total_brl}\n"
                f"- Payment Total: {payment_res.payment_total_brl}\n"
                f"- Payment Count: {payment_res.payment_count}\n"
                "Apply EC_POLICY_V1 rules and determine primary issue."
            )
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a customer support policy agent for Olist e-commerce."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback gracefully if API request fails
            print(f"[PolicyAgent LLM Warning]: {e}")
            return None

    def evaluate(self, order_seller_res: OrderSellerResult, payment_res: PaymentResult) -> PolicyResult:
        """
        Evaluates dispute cases based on EC_POLICY_V1 rules in strict priority order.

        :param order_seller_res: Result from OrderSellerAgent
        :param payment_res: Result from PaymentAgent
        :return: PolicyResult contract model
        """
        # Call LLM reasoning if API key is present
        _llm_reasoning = self._call_llm_reasoning(order_seller_res, payment_res)

        status = order_seller_res.order_status.lower()
        payment_total = payment_res.payment_total_brl
        freight_total = order_seller_res.freight_total_brl

        delivered_customer_date = order_seller_res.delivered_customer_date
        estimated_delivery_date = order_seller_res.estimated_delivery_date

        # Check if customer delivery was late
        is_late_delivery = False
        if delivered_customer_date and estimated_delivery_date:
            is_late_delivery = delivered_customer_date > estimated_delivery_date

        # Rule 1: canceled_order_paid
        if status == "canceled" and payment_total > 0:
            return PolicyResult(
                primary_issue="canceled_order_paid",
                case_status="action_required",
                confidence=0.95,
                root_cause_code="ORDER_CANCELED_AFTER_PAYMENT",
                responsible_parties=[
                    ResponsibleParty(party_type="platform", party_id="OLIST_PLATFORM")
                ],
                recommended_refund_brl=round(payment_total, 2),
                resolution_actions=["issue_full_refund"],
                policy_evidence_id="policy:ORDER_CANCELED_AFTER_PAYMENT"
            )

        # Rule 2: unavailable_order_paid
        if status == "unavailable" and payment_total > 0:
            return PolicyResult(
                primary_issue="unavailable_order_paid",
                case_status="action_required",
                confidence=0.95,
                root_cause_code="ORDER_UNAVAILABLE_AFTER_PAYMENT",
                responsible_parties=[
                    ResponsibleParty(party_type="platform", party_id="OLIST_PLATFORM")
                ],
                recommended_refund_brl=round(payment_total, 2),
                resolution_actions=["issue_full_refund"],
                policy_evidence_id="policy:ORDER_UNAVAILABLE_AFTER_PAYMENT"
            )

        # Rule 3: late_delivery_seller
        if is_late_delivery and len(order_seller_res.late_seller_ids) > 0:
            parties = [
                ResponsibleParty(party_type="seller", party_id=s_id)
                for s_id in order_seller_res.late_seller_ids
            ]
            return PolicyResult(
                primary_issue="late_delivery_seller",
                case_status="action_required",
                confidence=0.95,
                root_cause_code="SELLER_HANDOFF_AFTER_LIMIT",
                responsible_parties=parties,
                recommended_refund_brl=round(freight_total, 2),
                resolution_actions=["refund_freight"],
                policy_evidence_id="policy:SELLER_HANDOFF_AFTER_LIMIT"
            )

        # Rule 4: late_delivery_logistics
        if is_late_delivery and len(order_seller_res.late_seller_ids) == 0:
            return PolicyResult(
                primary_issue="late_delivery_logistics",
                case_status="action_required",
                confidence=0.95,
                root_cause_code="CARRIER_DELIVERED_AFTER_ESTIMATE",
                responsible_parties=[
                    ResponsibleParty(party_type="logistics_provider", party_id="LOGISTICS_PROVIDER")
                ],
                recommended_refund_brl=round(freight_total, 2),
                resolution_actions=["refund_freight"],
                policy_evidence_id="policy:CARRIER_DELIVERED_AFTER_ESTIMATE"
            )

        # Rule 5: valid_split_payment
        if payment_res.is_split_payment and payment_res.payment_matches_order_total:
            return PolicyResult(
                primary_issue="valid_split_payment",
                case_status="no_action",
                confidence=0.95,
                root_cause_code="MULTIPLE_PAYMENTS_RECONCILED",
                responsible_parties=[],
                recommended_refund_brl=0.0,
                resolution_actions=["explain_valid_split_payment"],
                policy_evidence_id="policy:MULTIPLE_PAYMENTS_RECONCILED"
            )

        # Rule 6: unsupported_late_claim (Default fallback)
        return PolicyResult(
            primary_issue="unsupported_late_claim",
            case_status="no_action",
            confidence=0.95,
            root_cause_code="DELIVERY_WITHIN_ESTIMATE",
            responsible_parties=[],
            recommended_refund_brl=0.0,
            resolution_actions=["reject_late_refund"],
            policy_evidence_id="policy:DELIVERY_WITHIN_ESTIMATE"
        )


class DeliveryAgent:
    """Agent alias/sub-component for checking delivery time frames."""

    def evaluate_delivery(self, delivered_customer_date: str, estimated_delivery_date: str) -> bool:
        """Returns True if delivery was after the estimated delivery date."""
        if delivered_customer_date and estimated_delivery_date:
            return delivered_customer_date > estimated_delivery_date
        return False
