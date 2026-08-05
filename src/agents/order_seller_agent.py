"""Order & Seller Agent implementation (Role 2)."""

from __future__ import annotations

from decimal import Decimal
from typing import Iterable, TypeVar

from src.contracts import OrderSellerResult
from src.repositories.order_repository import OrderItemRecord, OrderRepository


T = TypeVar("T")


def _unique(values: Iterable[T]) -> list[T]:
    """Deduplicate values while preserving stable source order."""
    return list(dict.fromkeys(values))


class OrderSellerAgent:
    """Analyze order entities, monetary totals, and seller handoff delays."""

    MAX_ENTITY_IDS = 5
    # Leave space in the final 10-ID evidence budget for payment and policy.
    MAX_AGENT_EVIDENCE_IDS = 7

    def __init__(self, repository: OrderRepository | None = None) -> None:
        self.repository = repository or OrderRepository()

    def analyze(self, order_id: str) -> OrderSellerResult:
        """Return the standardized Role 2 handoff for one Olist order."""
        order_id = order_id.strip()
        if not order_id:
            raise ValueError("order_id must be a non-empty string")

        order = self.repository.get_order(order_id)
        if order is None:
            # The shared contract has no error field.  An explicit unknown result
            # keeps the coordinator alive while avoiding fabricated evidence.
            return OrderSellerResult(order_id=order_id, order_status="unknown")

        items = list(self.repository.get_order_items(order_id))
        item_total = sum((item.price for item in items), Decimal("0"))
        freight_total = sum((item.freight_value for item in items), Decimal("0"))

        late_items = self._late_items(order.delivered_carrier_date, items)
        late_seller_ids = _unique(item.seller_id for item in late_items)
        seller_ids = _unique(item.seller_id for item in items)

        selected_items = items[: self.MAX_ENTITY_IDS]
        selected_sellers = seller_ids[: self.MAX_ENTITY_IDS]
        evidence_ids = self._build_evidence(
            order_id=order_id,
            all_items=items,
            late_items=late_items,
            seller_ids=seller_ids,
            late_seller_ids=late_seller_ids,
        )

        return OrderSellerResult(
            order_id=order_id,
            order_status=order.order_status,
            delivered_carrier_date=order.delivered_carrier_date,
            delivered_customer_date=order.delivered_customer_date,
            estimated_delivery_date=order.estimated_delivery_date,
            item_total_brl=round(float(item_total), 2),
            freight_total_brl=round(float(freight_total), 2),
            late_seller_ids=late_seller_ids[: self.MAX_ENTITY_IDS],
            # Entity IDs are raw IDs. Prefixes are reserved for evidence IDs.
            order_ids=[order_id],
            item_ids=[
                f"{order_id}:{item.order_item_id}" for item in selected_items
            ],
            seller_ids=selected_sellers,
            evidence_ids=evidence_ids,
        )

    @staticmethod
    def _late_items(
        delivered_carrier_date: str | None,
        items: list[OrderItemRecord],
    ) -> list[OrderItemRecord]:
        if delivered_carrier_date is None:
            return []
        return [
            item
            for item in items
            if item.shipping_limit_date is not None
            and delivered_carrier_date > item.shipping_limit_date
        ]

    def _build_evidence(
        self,
        *,
        order_id: str,
        all_items: list[OrderItemRecord],
        late_items: list[OrderItemRecord],
        seller_ids: list[str],
        late_seller_ids: list[str],
    ) -> list[str]:
        # Put policy-relevant late entities first. Remaining entities still
        # provide traceability when the order is not a seller-delay case.
        prioritized_items = _unique([*late_items, *all_items])
        prioritized_sellers = _unique([*late_seller_ids, *seller_ids])

        evidence = [f"order:{order_id}"]
        evidence.extend(
            f"item:{order_id}:{item.order_item_id}"
            for item in prioritized_items[: self.MAX_ENTITY_IDS]
        )
        evidence.extend(
            f"seller:{seller_id}"
            for seller_id in prioritized_sellers
            if self.repository.seller_exists(seller_id)
        )
        return _unique(evidence)[: self.MAX_AGENT_EVIDENCE_IDS]

