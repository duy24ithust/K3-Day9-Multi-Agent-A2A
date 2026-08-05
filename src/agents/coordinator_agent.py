"""
Coordinator Agent Module (Member 1 - Coordinator & Integration).

This module manages the execution flow and handoff protocols between:
- Order & Seller Agent (Member 2)
- Payment Agent (Member 3)
- Delivery & Policy Agent (Member 4)
- Verifier Agent (Member 5)
"""

import json
from typing import Dict, Any, List, Tuple
from src.contracts import (
    CaseInput,
    OrderSellerResult,
    PaymentResult,
    PolicyResult,
    FinalCaseOutput,
    Assessment,
    AffectedEntities,
    RootCauseAnalysis,
    CauseRank,
    FinancialResolution
)


class CoordinatorAgent:
    def __init__(
        self,
        order_seller_agent=None,
        payment_agent=None,
        policy_agent=None,
        verifier_agent=None
    ):
        self.order_seller_agent = order_seller_agent
        self.payment_agent = payment_agent
        self.policy_agent = policy_agent
        self.verifier_agent = verifier_agent

    def process_case(self, case_input: CaseInput) -> Tuple[FinalCaseOutput, List[Dict[str, Any]]]:
        """
        Orchestrate the end-to-end multi-agent dispute resolution workflow.
        Returns (FinalCaseOutput, trace_logs)
        """
        case_id = case_input.case_id
        order_id = case_input.customer_request.claimed_order_id
        trace_logs = []

        # 1. Handoff to Coordinator
        trace_logs.append({
            "case_id": case_id,
            "agent": "CoordinatorAgent",
            "action": "receive_case",
            "message": f"Case {case_id} received for order_id: {order_id}"
        })

        # 2. Handoff to Order & Seller Agent
        if self.order_seller_agent:
            order_seller_res: OrderSellerResult = self.order_seller_agent.analyze(order_id)
        else:
            # Fallback/stub if agent not yet injected
            order_seller_res = OrderSellerResult(
                order_id=order_id,
                order_status="unknown"
            )

        trace_logs.append({
            "case_id": case_id,
            "agent": "OrderSellerAgent",
            "action": "analyze_order_seller",
            "order_status": order_seller_res.order_status,
            "late_seller_ids": order_seller_res.late_seller_ids
        })

        # 3. Handoff to Payment Agent
        if self.payment_agent:
            payment_res: PaymentResult = self.payment_agent.analyze(order_id, order_seller_res.item_total_brl, order_seller_res.freight_total_brl)
        else:
            # Fallback/stub if agent not yet injected
            payment_res = PaymentResult(
                order_id=order_id,
                payment_total_brl=0.0
            )

        trace_logs.append({
            "case_id": case_id,
            "agent": "PaymentAgent",
            "action": "reconcile_payments",
            "payment_total_brl": payment_res.payment_total_brl,
            "is_split_payment": payment_res.is_split_payment
        })

        # 4. Handoff to Delivery & Policy Agent
        if self.policy_agent:
            policy_res: PolicyResult = self.policy_agent.evaluate(order_seller_res, payment_res)
        else:
            # Fallback/stub if agent not yet injected
            policy_res = PolicyResult(
                primary_issue="unsupported_late_claim",
                case_status="no_action",
                confidence=0.95,
                root_cause_code="DELIVERY_WITHIN_ESTIMATE",
                policy_evidence_id="policy:DELIVERY_WITHIN_ESTIMATE"
            )

        trace_logs.append({
            "case_id": case_id,
            "agent": "PolicyAgent",
            "action": "evaluate_policy",
            "primary_issue": policy_res.primary_issue,
            "case_status": policy_res.case_status,
            "recommended_refund_brl": policy_res.recommended_refund_brl
        })

        # 5. Assemble Evidence IDs (Max 10)
        evidence_ids = []
        evidence_ids.extend(order_seller_res.evidence_ids)
        evidence_ids.extend(payment_res.evidence_ids)
        if policy_res.policy_evidence_id and policy_res.policy_evidence_id not in evidence_ids:
            evidence_ids.append(policy_res.policy_evidence_id)
        
        # Deduplicate while preserving order & cap at 10
        seen = set()
        dedup_evidence = []
        for eid in evidence_ids:
            if eid not in seen:
                seen.add(eid)
                dedup_evidence.append(eid)
        evidence_ids = dedup_evidence[:10]

        # 6. Assemble Final Output
        final_output = FinalCaseOutput(
            case_id=case_id,
            assessment=Assessment(
                primary_issue=policy_res.primary_issue,
                case_status=policy_res.case_status,
                confidence=policy_res.confidence
            ),
            affected_entities=AffectedEntities(
                order_ids=order_seller_res.order_ids[:5],
                item_ids=order_seller_res.item_ids[:5],
                seller_ids=order_seller_res.seller_ids[:5],
                payment_ids=payment_res.payment_ids[:5]
            ),
            root_cause_analysis=RootCauseAnalysis(
                ranked_causes=[
                    CauseRank(cause_code=policy_res.root_cause_code, rank=1)
                ][:3],
                responsible_parties=policy_res.responsible_parties[:3]
            ),
            evidence_ids=evidence_ids,
            financial_resolution=FinancialResolution(
                currency="BRL",
                item_total_brl=round(order_seller_res.item_total_brl, 2),
                freight_total_brl=round(order_seller_res.freight_total_brl, 2),
                payment_total_brl=round(payment_res.payment_total_brl, 2),
                recommended_refund_brl=round(policy_res.recommended_refund_brl, 2)
            ),
            resolution_actions=policy_res.resolution_actions[:5]
        )

        # 7. Handoff to Verifier Agent
        if self.verifier_agent:
            verifier_res = self.verifier_agent.verify(final_output)
            trace_logs.append({
                "case_id": case_id,
                "agent": "VerifierAgent",
                "action": "verify_output",
                "is_valid": verifier_res.is_valid,
                "errors": verifier_res.validation_errors
            })
        else:
            trace_logs.append({
                "case_id": case_id,
                "agent": "VerifierAgent",
                "action": "verify_output",
                "is_valid": True,
                "errors": []
            })

        return final_output, trace_logs
