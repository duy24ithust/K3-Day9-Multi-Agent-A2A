"""Unit tests for Role 2's repository and OrderSellerAgent."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.agents.order_seller_agent import OrderSellerAgent
from src.repositories.order_repository import OrderRepository


ORDER_FIELDS = [
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
ITEM_FIELDS = [
    "order_id",
    "order_item_id",
    "product_id",
    "seller_id",
    "shipping_limit_date",
    "price",
    "freight_value",
]
SELLER_FIELDS = [
    "seller_id",
    "seller_zip_code_prefix",
    "seller_city",
    "seller_state",
]


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def agent(tmp_path: Path) -> OrderSellerAgent:
    _write_csv(
        tmp_path / OrderRepository.ORDERS_FILE,
        ORDER_FIELDS,
        [
            {
                "order_id": "on_time",
                "order_status": "delivered",
                "order_delivered_carrier_date": "2018-01-02 10:00:00",
                "order_delivered_customer_date": "2018-01-05 10:00:00",
                "order_estimated_delivery_date": "2018-01-06 00:00:00",
            },
            {
                "order_id": "late_multi",
                "order_status": "delivered",
                "order_delivered_carrier_date": "2018-02-03 10:00:00",
                "order_delivered_customer_date": "2018-02-10 10:00:00",
                "order_estimated_delivery_date": "2018-02-08 00:00:00",
            },
            {
                "order_id": "no_items",
                "order_status": "unavailable",
                "order_delivered_carrier_date": "",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2018-03-01 00:00:00",
            },
            {
                "order_id": "missing_dates",
                "order_status": "canceled",
                "order_delivered_carrier_date": "",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2018-04-01 00:00:00",
            },
        ],
    )
    _write_csv(
        tmp_path / OrderRepository.ITEMS_FILE,
        ITEM_FIELDS,
        [
            {
                "order_id": "on_time",
                "order_item_id": "1",
                "product_id": "p1",
                "seller_id": "seller_a",
                "shipping_limit_date": "2018-01-02 10:00:00",
                "price": "58.90",
                "freight_value": "13.29",
            },
            {
                "order_id": "late_multi",
                "order_item_id": "2",
                "product_id": "p2",
                "seller_id": "seller_late",
                "shipping_limit_date": "2018-02-01 09:00:00",
                "price": "20.20",
                "freight_value": "3.30",
            },
            {
                "order_id": "late_multi",
                "order_item_id": "1",
                "product_id": "p3",
                "seller_id": "seller_late",
                "shipping_limit_date": "2018-02-02 09:00:00",
                "price": "10.10",
                "freight_value": "2.20",
            },
            {
                "order_id": "late_multi",
                "order_item_id": "3",
                "product_id": "p4",
                "seller_id": "seller_on_time",
                "shipping_limit_date": "2018-02-04 09:00:00",
                "price": "30.30",
                "freight_value": "4.40",
            },
            {
                "order_id": "missing_dates",
                "order_item_id": "1",
                "product_id": "p5",
                "seller_id": "seller_a",
                "shipping_limit_date": "",
                "price": "1.00",
                "freight_value": "0.50",
            },
        ],
    )
    _write_csv(
        tmp_path / OrderRepository.SELLERS_FILE,
        SELLER_FIELDS,
        [
            {
                "seller_id": seller_id,
                "seller_zip_code_prefix": "10000",
                "seller_city": "sao paulo",
                "seller_state": "SP",
            }
            for seller_id in ("seller_a", "seller_late", "seller_on_time")
        ],
    )
    return OrderSellerAgent(OrderRepository(tmp_path))


def test_on_time_handoff_is_not_late(agent: OrderSellerAgent) -> None:
    result = agent.analyze("on_time")

    assert result.order_status == "delivered"
    assert result.late_seller_ids == []
    assert result.item_total_brl == 58.90
    assert result.freight_total_brl == 13.29
    assert result.order_ids == ["on_time"]
    assert result.item_ids == ["on_time:1"]
    assert result.seller_ids == ["seller_a"]
    assert result.evidence_ids == [
        "order:on_time",
        "item:on_time:1",
        "seller:seller_a",
    ]


def test_multiple_items_are_sorted_summed_and_classified(agent: OrderSellerAgent) -> None:
    result = agent.analyze("late_multi")

    assert result.item_ids == [
        "late_multi:1",
        "late_multi:2",
        "late_multi:3",
    ]
    assert result.seller_ids == ["seller_late", "seller_on_time"]
    assert result.late_seller_ids == ["seller_late"]
    assert result.item_total_brl == 60.60
    assert result.freight_total_brl == 9.90
    assert result.evidence_ids[:4] == [
        "order:late_multi",
        "item:late_multi:1",
        "item:late_multi:2",
        "item:late_multi:3",
    ]


def test_carrier_date_equal_to_limit_is_on_time(agent: OrderSellerAgent) -> None:
    assert agent.analyze("on_time").late_seller_ids == []


def test_order_without_items_has_zero_totals_and_empty_entities(
    agent: OrderSellerAgent,
) -> None:
    result = agent.analyze("no_items")

    assert result.item_total_brl == 0.0
    assert result.freight_total_brl == 0.0
    assert result.item_ids == []
    assert result.seller_ids == []
    assert result.late_seller_ids == []
    assert result.evidence_ids == ["order:no_items"]


def test_missing_dates_do_not_create_a_late_seller(agent: OrderSellerAgent) -> None:
    result = agent.analyze("missing_dates")

    assert result.delivered_carrier_date is None
    assert result.late_seller_ids == []


def test_unknown_order_returns_no_fabricated_entities_or_evidence(
    agent: OrderSellerAgent,
) -> None:
    result = agent.analyze("does_not_exist")

    assert result.order_status == "unknown"
    assert result.order_ids == []
    assert result.item_ids == []
    assert result.seller_ids == []
    assert result.evidence_ids == []


def test_empty_order_id_is_rejected(agent: OrderSellerAgent) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        agent.analyze("   ")


def test_missing_required_csv_fails_fast(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Required Olist CSV"):
        OrderRepository(tmp_path)

