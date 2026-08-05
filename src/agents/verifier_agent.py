"""
Verifier Agent module for multi-agent e-commerce dispute resolution.
Validates FinalCaseOutput against schema bounds and business constraints.
"""

from typing import List
from src.contracts import FinalCaseOutput, VerifierResult


class VerifierAgent:
    """Agent responsible for checking constraint compliance of final outputs."""

    def verify(self, output: FinalCaseOutput) -> VerifierResult:
        """
        Validates FinalCaseOutput against all problem constraints.

        :param output: FinalCaseOutput contract instance
        :return: VerifierResult detailing validity and any validation error messages.
        """
        errors: List[str] = []

        # Check confidence bounds
        if not (0.0 <= output.assessment.confidence <= 1.0):
            errors.append(f"Confidence {output.assessment.confidence} out of bounds [0.0, 1.0]")

        # Check case_status valid values
        if output.assessment.case_status not in ["action_required", "no_action"]:
            errors.append(f"Invalid case_status: {output.assessment.case_status}")

        # Check entity collection limits
        if len(output.affected_entities.order_ids) > 5:
            errors.append(f"order_ids exceeds max length 5: {len(output.affected_entities.order_ids)}")
        if len(output.affected_entities.item_ids) > 5:
            errors.append(f"item_ids exceeds max length 5: {len(output.affected_entities.item_ids)}")
        if len(output.affected_entities.seller_ids) > 5:
            errors.append(f"seller_ids exceeds max length 5: {len(output.affected_entities.seller_ids)}")
        if len(output.affected_entities.payment_ids) > 5:
            errors.append(f"payment_ids exceeds max length 5: {len(output.affected_entities.payment_ids)}")

        # Check evidence limit
        if len(output.evidence_ids) > 10:
            errors.append(f"evidence_ids exceeds max length 10: {len(output.evidence_ids)}")

        # Check root causes & responsible parties limits
        if len(output.root_cause_analysis.ranked_causes) > 3:
            errors.append(f"ranked_causes exceeds max length 3: {len(output.root_cause_analysis.ranked_causes)}")
        if len(output.root_cause_analysis.responsible_parties) > 3:
            errors.append(f"responsible_parties exceeds max length 3: {len(output.root_cause_analysis.responsible_parties)}")

        # Check resolution actions limit
        if len(output.resolution_actions) > 5:
            errors.append(f"resolution_actions exceeds max length 5: {len(output.resolution_actions)}")

        # Financial values non-negative checks
        if output.financial_resolution.item_total_brl < 0:
            errors.append("item_total_brl cannot be negative")
        if output.financial_resolution.freight_total_brl < 0:
            errors.append("freight_total_brl cannot be negative")
        if output.financial_resolution.payment_total_brl < 0:
            errors.append("payment_total_brl cannot be negative")
        if output.financial_resolution.recommended_refund_brl < 0:
            errors.append("recommended_refund_brl cannot be negative")

        is_valid = (len(errors) == 0)
        return VerifierResult(is_valid=is_valid, validation_errors=errors)
