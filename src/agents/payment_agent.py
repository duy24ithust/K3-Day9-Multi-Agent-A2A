"""
Payment Agent module for multi-agent e-commerce dispute resolution.
Responsible for reading payment data, calculating payment totals, checking split payments,
reconciling payment against (item_total + freight_total), and generating payment evidence.
"""

from typing import List, Optional
from src.contracts import PaymentResult
from src.repositories.payment_repository import PaymentRepository


class PaymentAgent:
    """Agent responsible for payment validation and financial reconciliation."""

    def __init__(self, repository: Optional[PaymentRepository] = None):
        if repository is None:
            repository = PaymentRepository()
        self.repository = repository

    def process_payment(
        self,
        order_id: str,
        item_total_brl: float = 0.0,
        freight_total_brl: float = 0.0
    ) -> PaymentResult:
        """
        Processes payment rows for an order, reconciles against order total, and builds PaymentResult.

        :param order_id: Olist order ID
        :param item_total_brl: Total price of items in BRL (from OrderSellerAgent)
        :param freight_total_brl: Total freight cost in BRL (from OrderSellerAgent)
        :return: PaymentResult Pydantic contract model
        """
        clean_order_id = order_id.strip('"\'' )
        payments = self.repository.get_payments_by_order_id(clean_order_id)

        payment_count = len(payments)
        raw_total = sum(p['payment_value'] for p in payments)
        payment_total_brl = round(raw_total, 2)

        # Expected total from order seller agent
        expected_total = round(item_total_brl + freight_total_brl, 2)

        # Reconcile within 0.10 BRL tolerance
        payment_matches_order_total = abs(payment_total_brl - expected_total) <= 0.10

        # Split payment condition: >= 2 payment rows
        is_split_payment = payment_count >= 2

        # Build IDs
        payment_ids: List[str] = []
        evidence_ids: List[str] = []

        for p in sorted(payments, key=lambda x: x['payment_sequential']):
            seq = p['payment_sequential']
            payment_ids.append(f"{clean_order_id}:{seq}")
            evidence_ids.append(f"payment:{clean_order_id}:{seq}")

        return PaymentResult(
            order_id=clean_order_id,
            payment_total_brl=payment_total_brl,
            payment_count=payment_count,
            payment_matches_order_total=payment_matches_order_total,
            is_split_payment=is_split_payment,
            payment_ids=payment_ids,
            evidence_ids=evidence_ids
        )
