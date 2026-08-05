"""
Unit tests for PaymentAgent and PaymentRepository.
"""

import unittest
from unittest.mock import MagicMock
from src.agents.payment_agent import PaymentAgent
from src.repositories.payment_repository import PaymentRepository
from src.contracts import PaymentResult


class TestPaymentAgent(unittest.TestCase):

    def setUp(self):
        self.mock_repo = MagicMock(spec=PaymentRepository)
        self.agent = PaymentAgent(repository=self.mock_repo)

    def test_single_payment_exact_match(self):
        self.mock_repo.get_payments_by_order_id.return_value = [
            {'payment_sequential': 1, 'payment_type': 'credit_card', 'payment_installments': 1, 'payment_value': 100.00}
        ]

        result = self.agent.process_payment("order_123", item_total_brl=85.00, freight_total_brl=15.00)

        self.assertIsInstance(result, PaymentResult)
        self.assertEqual(result.order_id, "order_123")
        self.assertEqual(result.payment_total_brl, 100.00)
        self.assertEqual(result.payment_count, 1)
        self.assertFalse(result.is_split_payment)
        self.assertTrue(result.payment_matches_order_total)
        self.assertEqual(result.payment_ids, ["order_123:1"])
        self.assertEqual(result.evidence_ids, ["payment:order_123:1"])

    def test_split_payment_tolerance_match(self):
        # Order total = 100.00, payment total = 100.10 (diff = 0.10, within tolerance)
        self.mock_repo.get_payments_by_order_id.return_value = [
            {'payment_sequential': 1, 'payment_type': 'voucher', 'payment_installments': 1, 'payment_value': 50.00},
            {'payment_sequential': 2, 'payment_type': 'credit_card', 'payment_installments': 2, 'payment_value': 50.10}
        ]

        result = self.agent.process_payment("order_456", item_total_brl=80.00, freight_total_brl=20.00)

        self.assertEqual(result.payment_total_brl, 100.10)
        self.assertEqual(result.payment_count, 2)
        self.assertTrue(result.is_split_payment)
        self.assertTrue(result.payment_matches_order_total)
        self.assertEqual(result.payment_ids, ["order_456:1", "order_456:2"])
        self.assertEqual(result.evidence_ids, ["payment:order_456:1", "payment:order_456:2"])

    def test_payment_mismatch_exceeds_tolerance(self):
        # Order total = 100.00, payment total = 100.15 (diff = 0.15 > 0.10)
        self.mock_repo.get_payments_by_order_id.return_value = [
            {'payment_sequential': 1, 'payment_type': 'credit_card', 'payment_installments': 1, 'payment_value': 100.15}
        ]

        result = self.agent.process_payment("order_789", item_total_brl=80.00, freight_total_brl=20.00)

        self.assertEqual(result.payment_total_brl, 100.15)
        self.assertFalse(result.payment_matches_order_total)

    def test_empty_payments(self):
        self.mock_repo.get_payments_by_order_id.return_value = []

        result = self.agent.process_payment("order_empty", item_total_brl=50.00, freight_total_brl=10.00)

        self.assertEqual(result.payment_total_brl, 0.0)
        self.assertEqual(result.payment_count, 0)
        self.assertFalse(result.is_split_payment)
        self.assertFalse(result.payment_matches_order_total)
        self.assertEqual(result.payment_ids, [])
        self.assertEqual(result.evidence_ids, [])


if __name__ == '__main__':
    unittest.main()
