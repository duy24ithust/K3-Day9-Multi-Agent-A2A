"""
Delivery Agent module for multi-agent e-commerce dispute resolution.
Analyzes actual vs estimated delivery timestamps and carrier handoff deadlines.
"""

from typing import Optional
from src.contracts import OrderSellerResult, DeliveryResult


class DeliveryAgent:
    """Agent responsible for checking delivery time frames and carrier handoffs."""

    def analyze(self, order_seller_res: OrderSellerResult) -> DeliveryResult:
        """
        Analyzes delivery dates and determines if delivery or seller handoff was late.

        :param order_seller_res: Result from OrderSellerAgent
        :return: DeliveryResult contract
        """
        delivered_customer_date = order_seller_res.delivered_customer_date
        estimated_delivery_date = order_seller_res.estimated_delivery_date

        is_late_delivery = False
        if delivered_customer_date and estimated_delivery_date:
            is_late_delivery = delivered_customer_date > estimated_delivery_date

        late_seller_ids = order_seller_res.late_seller_ids
        is_seller_late = len(late_seller_ids) > 0

        return DeliveryResult(
            order_id=order_seller_res.order_id,
            is_late_delivery=is_late_delivery,
            is_seller_late=is_seller_late,
            late_seller_ids=late_seller_ids
        )
