"""
Unit Tests for VerifierAgent (Member 5).
"""

import sys
import os
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.contracts import (
    FinalCaseOutput,
    Assessment,
    AffectedEntities,
    RootCauseAnalysis,
    CauseRank,
    ResponsibleParty,
    FinancialResolution
)
from src.agents.verifier_agent import VerifierAgent


class TestVerifierAgent(unittest.TestCase):
    def setUp(self):
        self.verifier = VerifierAgent()

    def test_valid_output_passes(self):
        valid_output = FinalCaseOutput(
            case_id="EC_001",
            assessment=Assessment(
                primary_issue="late_delivery_seller",
                case_status="action_required",
                confidence=0.98
            ),
            affected_entities=AffectedEntities(
                order_ids=["e2a03ccf5ea816036608b2d8c3ab8e60"],
                item_ids=["e2a03ccf5ea816036608b2d8c3ab8e60:1"],
                seller_ids=["f7496d659ca9fdaf323c0aae84176632"],
                payment_ids=["e2a03ccf5ea816036608b2d8c3ab8e60:1"]
            ),
            root_cause_analysis=RootCauseAnalysis(
                ranked_causes=[CauseRank(cause_code="SELLER_HANDOFF_AFTER_LIMIT", rank=1)],
                responsible_parties=[ResponsibleParty(party_type="seller", party_id="f7496d659ca9fdaf323c0aae84176632")]
            ),
            evidence_ids=[
                "order:e2a03ccf5ea816036608b2d8c3ab8e60",
                "item:e2a03ccf5ea816036608b2d8c3ab8e60:1",
                "payment:e2a03ccf5ea816036608b2d8c3ab8e60:1",
                "seller:f7496d659ca9fdaf323c0aae84176632",
                "policy:SELLER_HANDOFF_AFTER_LIMIT"
            ],
            financial_resolution=FinancialResolution(
                currency="BRL",
                item_total_brl=119.9,
                freight_total_brl=12.04,
                payment_total_brl=131.94,
                recommended_refund_brl=12.04
            ),
            resolution_actions=["refund_freight"]
        )

        res = self.verifier.verify(valid_output)
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.validation_errors), 0)

    def test_exceeding_evidence_limit_fails(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            FinalCaseOutput(
                case_id="EC_002",
                assessment=Assessment(primary_issue="unsupported_late_claim", case_status="no_action", confidence=0.98),
                affected_entities=AffectedEntities(order_ids=["ord1"]),
                root_cause_analysis=RootCauseAnalysis(ranked_causes=[CauseRank(cause_code="DELIVERY_WITHIN_ESTIMATE", rank=1)]),
                evidence_ids=[f"ev_{i}" for i in range(12)],  # 12 evidence IDs exceeds limit 10
                financial_resolution=FinancialResolution(currency="BRL", item_total_brl=0, freight_total_brl=0, payment_total_brl=0, recommended_refund_brl=0),
                resolution_actions=["reject_late_refund"]
            )


if __name__ == "__main__":
    unittest.main()
