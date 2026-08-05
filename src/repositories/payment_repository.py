"""
Payment Repository for accessing olist_order_payments_dataset.csv data.
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional


class PaymentRepository:
    """Repository for querying payment data from Olist dataset."""

    def __init__(self, csv_path: Optional[str] = None):
        if csv_path is None:
            # Default path relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            csv_path = os.path.join(base_dir, "data", "olist_order_payments_dataset.csv")

        self.csv_path = csv_path
        self._payments_by_order: Dict[str, List[Dict[str, Any]]] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Loads CSV data and indexes payments by order_id for O(1) lookup."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Payment CSV dataset not found at: {self.csv_path}")

        df = pd.read_csv(self.csv_path, dtype={
            'order_id': str,
            'payment_sequential': int,
            'payment_type': str,
            'payment_installments': int,
            'payment_value': float
        })

        # Strip quotes or whitespace if present
        df['order_id'] = df['order_id'].str.strip('"\'' )

        for _, row in df.iterrows():
            order_id = row['order_id']
            payment_info = {
                'payment_sequential': int(row['payment_sequential']),
                'payment_type': str(row['payment_type']),
                'payment_installments': int(row['payment_installments']),
                'payment_value': float(row['payment_value'])
            }
            if order_id not in self._payments_by_order:
                self._payments_by_order[order_id] = []
            self._payments_by_order[order_id].append(payment_info)

    def get_payments_by_order_id(self, order_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all payment rows for a given order_id.

        :param order_id: Clean string order_id
        :return: List of payment dicts containing payment_sequential, payment_type, etc.
        """
        clean_order_id = str(order_id).strip().strip('"\'' ).strip()
        return self._payments_by_order.get(clean_order_id, [])
