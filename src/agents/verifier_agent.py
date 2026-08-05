"""
Verifier Agent Module (Member 5).

Validates FinalCaseOutput objects against EC_POLICY_V1 schema constraints and entity bounds.
"""

from typing import List
from src.contracts import FinalCaseOutput, VerifierResult


class VerifierAgent:
    """Agent responsible for checking compliance of output JSON schema and constraints."""

    def verify(self, output: FinalCaseOutput) -> VerifierResult:
        errors: List[str] = []

        # Check entity bounds
        if len(output.affected_entities.order_ids) > 5:
            errors.append(f"order_ids exceeds max limit of 5 (found {len(output.affected_entities.order_ids)})")
        if len(output.affected_entities.item_ids) > 5:
            errors.append(f"item_ids exceeds max limit of 5 (found {len(output.affected_entities.item_ids)})")
        if len(output.affected_entities.seller_ids) > 5:
            errors.append(f"seller_ids exceeds max limit of 5 (found {len(output.affected_entities.seller_ids)})")
        if len(output.affected_entities.payment_ids) > 5:
            errors.append(f"payment_ids exceeds max limit of 5 (found {len(output.affected_entities.payment_ids)})")

        # Check evidence limit
        if len(output.evidence_ids) > 10:
            errors.append(f"evidence_ids exceeds max limit of 10 (found {len(output.evidence_ids)})")

        # Check root cause bounds
        if len(output.root_cause_analysis.ranked_causes) > 3:
            errors.append(f"ranked_causes exceeds max limit of 3 (found {len(output.root_cause_analysis.ranked_causes)})")
        if len(output.root_cause_analysis.responsible_parties) > 3:
            errors.append(f"responsible_parties exceeds max limit of 3 (found {len(output.root_cause_analysis.responsible_parties)})")

        # Check actions limit
        if len(output.resolution_actions) > 5:
            errors.append(f"resolution_actions exceeds max limit of 5 (found {len(output.resolution_actions)})")

        # Check confidence range [0.0, 1.0]
        conf = output.assessment.confidence
        if not (0.0 <= conf <= 1.0):
            errors.append(f"confidence {conf} out of range [0.0, 1.0]")

        is_valid = len(errors) == 0
        return VerifierResult(is_valid=is_valid, validation_errors=errors)
