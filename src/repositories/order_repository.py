"""
Order Repository for accessing olist_orders_dataset.csv, olist_order_items_dataset.csv,
and olist_sellers_dataset.csv data.
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional


class OrderRepository:
    """Repository for querying order, item, and seller data from Olist dataset."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "data")

        self.data_dir = data_dir
        self._orders_by_id: Dict[str, Dict[str, Any]] = {}
        self._items_by_order: Dict[str, List[Dict[str, Any]]] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Loads and indexes orders and order_items CSV data."""
        orders_csv = os.path.join(self.data_dir, "olist_orders_dataset.csv")
        items_csv = os.path.join(self.data_dir, "olist_order_items_dataset.csv")

        if not os.path.exists(orders_csv):
            raise FileNotFoundError(f"Orders CSV dataset not found at: {orders_csv}")
        if not os.path.exists(items_csv):
            raise FileNotFoundError(f"Order items CSV dataset not found at: {items_csv}")

        # Load orders
        orders_df = pd.read_csv(orders_csv, dtype=str)
        orders_df['order_id'] = orders_df['order_id'].str.strip('"\'' )

        for _, row in orders_df.iterrows():
            order_id = row['order_id']
            self._orders_by_id[order_id] = {
                'order_id': order_id,
                'customer_id': row.get('customer_id'),
                'order_status': str(row.get('order_status', '')).strip(),
                'delivered_carrier_date': row.get('order_delivered_carrier_date') if pd.notna(row.get('order_delivered_carrier_date')) else None,
                'delivered_customer_date': row.get('order_delivered_customer_date') if pd.notna(row.get('order_delivered_customer_date')) else None,
                'estimated_delivery_date': row.get('order_estimated_delivery_date') if pd.notna(row.get('order_estimated_delivery_date')) else None,
            }

        # Load order items
        items_df = pd.read_csv(items_csv, dtype={
            'order_id': str,
            'order_item_id': int,
            'product_id': str,
            'seller_id': str,
            'shipping_limit_date': str,
            'price': float,
            'freight_value': float
        })
        items_df['order_id'] = items_df['order_id'].str.strip('"\'' )

        for _, row in items_df.iterrows():
            order_id = row['order_id']
            item_info = {
                'order_item_id': int(row['order_item_id']),
                'product_id': str(row['product_id']).strip('"\'' ),
                'seller_id': str(row['seller_id']).strip('"\'' ),
                'shipping_limit_date': str(row['shipping_limit_date']).strip('"\'' ) if pd.notna(row['shipping_limit_date']) else None,
                'price': float(row['price']),
                'freight_value': float(row['freight_value'])
            }
            if order_id not in self._items_by_order:
                self._items_by_order[order_id] = []
            self._items_by_order[order_id].append(item_info)

    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves order details for a given order_id."""
        clean_id = str(order_id).strip().strip('"\'' ).strip()
        return self._orders_by_id.get(clean_id)

    def get_order_items(self, order_id: str) -> List[Dict[str, Any]]:
        """Retrieves all item rows for a given order_id."""
        clean_id = str(order_id).strip().strip('"\'' ).strip()
        return self._items_by_order.get(clean_id, [])
