"""Read-only access to Olist order, item, and seller data.

The repository loads each CSV once and exposes small immutable records to the
OrderSellerAgent.  Keeping CSV access here makes the agent deterministic and
allows unit tests to inject a temporary data directory.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class OrderRecord:
    order_id: str
    order_status: str
    delivered_carrier_date: Optional[str]
    delivered_customer_date: Optional[str]
    estimated_delivery_date: Optional[str]


@dataclass(frozen=True)
class OrderItemRecord:
    order_id: str
    order_item_id: str
    seller_id: str
    shipping_limit_date: Optional[str]
    price: Decimal
    freight_value: Decimal


@dataclass(frozen=True)
class SellerRecord:
    seller_id: str
    zip_code_prefix: str
    city: str
    state: str


def _optional_text(value: Optional[str]) -> Optional[str]:
    """Normalize empty CSV cells to None without changing timestamps."""
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _money(value: Optional[str], *, column: str, order_id: str) -> Decimal:
    """Parse a required monetary cell and report useful source context."""
    try:
        return Decimal((value or "").strip())
    except InvalidOperation as exc:
        raise ValueError(
            f"Invalid {column} value for order {order_id!r}: {value!r}"
        ) from exc


class OrderRepository:
    """In-memory index over the three CSV files owned by Role 2."""

    ORDERS_FILE = "olist_orders_dataset.csv"
    ITEMS_FILE = "olist_order_items_dataset.csv"
    SELLERS_FILE = "olist_sellers_dataset.csv"

    def __init__(self, data_dir: str | Path = "data") -> None:
        self.data_dir = Path(data_dir)
        self._orders: dict[str, OrderRecord] = {}
        self._items_by_order: dict[str, list[OrderItemRecord]] = {}
        self._sellers: dict[str, SellerRecord] = {}
        self._load()

    def _load(self) -> None:
        self._load_orders(self.data_dir / self.ORDERS_FILE)
        self._load_items(self.data_dir / self.ITEMS_FILE)
        self._load_sellers(self.data_dir / self.SELLERS_FILE)

    @staticmethod
    def _open_csv(path: Path):
        if not path.is_file():
            raise FileNotFoundError(f"Required Olist CSV not found: {path}")
        return path.open("r", encoding="utf-8-sig", newline="")

    def _load_orders(self, path: Path) -> None:
        with self._open_csv(path) as csv_file:
            for row in csv.DictReader(csv_file):
                order_id = row["order_id"].strip()
                self._orders[order_id] = OrderRecord(
                    order_id=order_id,
                    order_status=row["order_status"].strip(),
                    delivered_carrier_date=_optional_text(
                        row.get("order_delivered_carrier_date")
                    ),
                    delivered_customer_date=_optional_text(
                        row.get("order_delivered_customer_date")
                    ),
                    estimated_delivery_date=_optional_text(
                        row.get("order_estimated_delivery_date")
                    ),
                )

    def _load_items(self, path: Path) -> None:
        with self._open_csv(path) as csv_file:
            for row in csv.DictReader(csv_file):
                order_id = row["order_id"].strip()
                item = OrderItemRecord(
                    order_id=order_id,
                    order_item_id=row["order_item_id"].strip(),
                    seller_id=row["seller_id"].strip(),
                    shipping_limit_date=_optional_text(row.get("shipping_limit_date")),
                    price=_money(row.get("price"), column="price", order_id=order_id),
                    freight_value=_money(
                        row.get("freight_value"),
                        column="freight_value",
                        order_id=order_id,
                    ),
                )
                self._items_by_order.setdefault(order_id, []).append(item)

        for items in self._items_by_order.values():
            items.sort(key=self._item_sort_key)

    def _load_sellers(self, path: Path) -> None:
        with self._open_csv(path) as csv_file:
            for row in csv.DictReader(csv_file):
                seller_id = row["seller_id"].strip()
                self._sellers[seller_id] = SellerRecord(
                    seller_id=seller_id,
                    zip_code_prefix=(row.get("seller_zip_code_prefix") or "").strip(),
                    city=(row.get("seller_city") or "").strip(),
                    state=(row.get("seller_state") or "").strip(),
                )

    @staticmethod
    def _item_sort_key(item: OrderItemRecord) -> tuple[int, int | str]:
        try:
            return (0, int(item.order_item_id))
        except ValueError:
            return (1, item.order_item_id)

    def get_order(self, order_id: str) -> Optional[OrderRecord]:
        return self._orders.get(order_id)

    def get_order_items(self, order_id: str) -> tuple[OrderItemRecord, ...]:
        return tuple(self._items_by_order.get(order_id, ()))

    def get_seller(self, seller_id: str) -> Optional[SellerRecord]:
        return self._sellers.get(seller_id)

    def seller_exists(self, seller_id: str) -> bool:
        return seller_id in self._sellers

