"""
Order & Seller Agent module for multi-agent e-commerce dispute resolution.
Responsible for analyzing order status, items, freight cost, seller handoff deadlines,
and generating order/item/seller evidence.
"""

from typing import List, Optional, Set
from src.contracts import OrderSellerResult
from src.repositories.order_repository import OrderRepository


class OrderSellerAgent:
    """Agent responsible for order status, item aggregation, and seller handoff deadline verification."""

    def __init__(self, repository: Optional[OrderRepository] = None):
        if repository is None:
            repository = OrderRepository()
        self.repository = repository

    def analyze(self, order_id: str) -> OrderSellerResult:
        """
        Analyzes order details, item totals, freight totals, late seller handoffs, and IDs.

        :param order_id: Olist order ID
        :return: OrderSellerResult contract object
        """
        clean_order_id = str(order_id).strip().strip('"\'' ).strip()
        order_info = self.repository.get_order_by_id(clean_order_id)
        items = self.repository.get_order_items(clean_order_id)

        if not order_info:
            return OrderSellerResult(
                order_id=clean_order_id,
                order_status="unknown"
            )

        order_status = order_info['order_status']
        delivered_carrier_date = order_info['delivered_carrier_date']
        delivered_customer_date = order_info['delivered_customer_date']
        estimated_delivery_date = order_info['estimated_delivery_date']

        item_total_brl = round(sum(i['price'] for i in items), 2)
        freight_total_brl = round(sum(i['freight_value'] for i in items), 2)

        late_seller_ids: List[str] = []
        late_sellers_set: Set[str] = set()

        if delivered_carrier_date:
            for item in items:
                limit_date = item.get('shipping_limit_date')
                seller_id = item.get('seller_id')
                if limit_date and seller_id:
                    # String comparison ISO timestamps in CSV
                    if delivered_carrier_date > limit_date:
                        if seller_id not in late_sellers_set:
                            late_sellers_set.add(seller_id)
                            late_seller_ids.append(seller_id)

        order_ids = [clean_order_id]
        item_ids = [f"{clean_order_id}:{i['order_item_id']}" for i in items]
        
        # Deduplicated seller IDs
        seller_ids_set = set()
        seller_ids = []
        for i in items:
            s_id = i.get('seller_id')
            if s_id and s_id not in seller_ids_set:
                seller_ids_set.add(s_id)
                seller_ids.append(s_id)

        # Evidence IDs: order:<id>, item:<id>:<item_id>, seller:<seller_id>
        evidence_ids: List[str] = [f"order:{clean_order_id}"]
        for item in items:
            evidence_ids.append(f"item:{clean_order_id}:{item['order_item_id']}")
        for s_id in seller_ids:
            evidence_ids.append(f"seller:{s_id}")

        return OrderSellerResult(
            order_id=clean_order_id,
            order_status=order_status,
            delivered_carrier_date=delivered_carrier_date,
            delivered_customer_date=delivered_customer_date,
            estimated_delivery_date=estimated_delivery_date,
            item_total_brl=item_total_brl,
            freight_total_brl=freight_total_brl,
            late_seller_ids=late_seller_ids,
            order_ids=order_ids,
            item_ids=item_ids,
            seller_ids=seller_ids,
            evidence_ids=evidence_ids
        )
