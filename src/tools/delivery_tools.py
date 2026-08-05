import os
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel, Field
from src.contracts import ResponsibleParty


class DeliveryAssessment(BaseModel):
    """Clean assessment structure for delivery analysis."""
    is_delivered_late: bool = Field(..., description="True if customer delivery date > estimated delivery date")
    seller_handoff_late: bool = Field(..., description="True if carrier handoff date > shipping limit date")
    suggested_issue: Optional[str] = Field(None, description="Candidate primary issue")
    suggested_root_cause: Optional[str] = Field(None, description="Candidate root cause code")
    responsible_party: Optional[ResponsibleParty] = Field(None, description="Responsible party object or None")


class DeliveryCheckResult(BaseModel):
    """Concise Pydantic model representing delivery analysis output."""
    agent_name: str = Field(default="DeliveryAgent", description="Name of the agent")
    order_id: str = Field(..., description="Claimed Olist order ID")
    delivery_assessment: DeliveryAssessment
    evidence_ids: List[str] = Field(default_factory=list, description="Ground truth evidence IDs")
    error: Optional[str] = Field(None, description="Error message if not found")


def analyze_delivery_with_pandas(order_id: str, data_dir: str = "data") -> DeliveryCheckResult:
    """
    Pandas-based tool to load and filter Olist datasets, returning clean Pydantic DeliveryCheckResult.
    """
    orders_csv = os.path.join(data_dir, "olist_orders_dataset.csv")
    items_csv = os.path.join(data_dir, "olist_order_items_dataset.csv")

    if not os.path.exists(orders_csv):
        return DeliveryCheckResult(
            order_id=order_id,
            delivery_assessment=DeliveryAssessment(
                is_delivered_late=False,
                seller_handoff_late=False
            ),
            error=f"Dataset file {orders_csv} does not exist."
        )

    orders_df = pd.read_csv(orders_csv)
    matched_orders = orders_df[orders_df["order_id"] == order_id]

    if matched_orders.empty:
        return DeliveryCheckResult(
            order_id=order_id,
            delivery_assessment=DeliveryAssessment(
                is_delivered_late=False,
                seller_handoff_late=False
            ),
            error=f"Order ID {order_id} not found in orders dataset."
        )

    order_row = matched_orders.iloc[0]
    order_status = str(order_row["order_status"]) if pd.notna(order_row["order_status"]) else None
    delivered_carrier = str(order_row["order_delivered_carrier_date"]) if pd.notna(order_row["order_delivered_carrier_date"]) else None
    delivered_customer = str(order_row["order_delivered_customer_date"]) if pd.notna(order_row["order_delivered_customer_date"]) else None
    estimated_delivery = str(order_row["order_estimated_delivery_date"]) if pd.notna(order_row["order_estimated_delivery_date"]) else None

    # Load items dataset if available
    seller_ids: List[str] = []
    item_ids: List[str] = []
    max_shipping_limit: Optional[str] = None

    if os.path.exists(items_csv):
        items_df = pd.read_csv(items_csv)
        matched_items = items_df[items_df["order_id"] == order_id]

        if not matched_items.empty:
            if "seller_id" in matched_items.columns:
                seller_ids = [str(sid) for sid in matched_items["seller_id"].dropna().unique().tolist()]
            
            if "order_item_id" in matched_items.columns:
                item_ids = [f"{order_id}:{item_seq}" for item_seq in matched_items["order_item_id"].tolist()]

            if "shipping_limit_date" in matched_items.columns:
                limits = matched_items["shipping_limit_date"].dropna().tolist()
                if limits:
                    max_shipping_limit = max(limits)

    # Calculate boolean delivery metrics
    is_delivered_late = False
    if delivered_customer and estimated_delivery:
        is_delivered_late = str(delivered_customer) > str(estimated_delivery)

    is_seller_late_handoff = False
    if delivered_carrier and max_shipping_limit:
        is_seller_late_handoff = str(delivered_carrier) > str(max_shipping_limit)

    # Determine candidate primary issue, root cause & responsible party
    suggested_issue = None
    suggested_root_cause = None
    responsible_party: Optional[ResponsibleParty] = None

    if order_status in ["canceled", "unavailable"]:
        suggested_issue = f"{order_status}_order_paid"
        suggested_root_cause = f"ORDER_{order_status.upper()}_AFTER_PAYMENT"
        responsible_party = ResponsibleParty(party_type="platform", party_id="OLIST_PLATFORM")
    elif not is_delivered_late:
        suggested_issue = "unsupported_late_claim"
        suggested_root_cause = "DELIVERY_WITHIN_ESTIMATE"
        responsible_party = None
    elif is_seller_late_handoff:
        suggested_issue = "late_delivery_seller"
        suggested_root_cause = "SELLER_HANDOFF_AFTER_LIMIT"
        primary_seller = seller_ids[0] if seller_ids else "UNKNOWN_SELLER"
        responsible_party = ResponsibleParty(party_type="seller", party_id=primary_seller)
    else:
        suggested_issue = "late_delivery_logistics"
        suggested_root_cause = "CARRIER_DELIVERED_AFTER_ESTIMATE"
        responsible_party = ResponsibleParty(party_type="logistics_provider", party_id="LOGISTICS_PROVIDER")

    # Evidence IDs construction matching spec: order:<id>, seller:<id>, item:<id>:<seq>, policy:<root_cause>
    evidence_ids = [f"order:{order_id}"]
    for seller_id in seller_ids:
        evidence_ids.append(f"seller:{seller_id}")
    for item_id in item_ids:
        evidence_ids.append(f"item:{item_id}")
    if suggested_root_cause:
        evidence_ids.append(f"policy:{suggested_root_cause}")

    # Remove duplicates while keeping order & cap at 10
    dedup_evidences = list(dict.fromkeys(evidence_ids))[:10]

    return DeliveryCheckResult(
        agent_name="DeliveryAgent",
        order_id=order_id,
        delivery_assessment=DeliveryAssessment(
            is_delivered_late=is_delivered_late,
            seller_handoff_late=is_seller_late_handoff,
            suggested_issue=suggested_issue,
            suggested_root_cause=suggested_root_cause,
            responsible_party=responsible_party
        ),
        evidence_ids=dedup_evidences
    )
