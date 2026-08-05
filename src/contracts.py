"""
Data Contracts for E-commerce Multi-Agent Dispute Resolution System.

This module defines standard Pydantic models for data interchange between:
- Member 1 (Coordinator & Integration)
- Member 2 (Order & Seller Agent)
- Member 3 (Payment Agent)
- Member 4 (Delivery & Policy Agent)
- Member 5 (Verifier & Documentation)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CustomerRequest(BaseModel):
    """Details of the customer claim contained within CaseInput."""
    language: str = Field(..., description="Language code of customer claim, e.g., 'vi'")
    message: str = Field(..., description="Customer claim text message")
    claimed_order_id: str = Field(..., description="Olist order ID claimed by customer")


class CaseInput(BaseModel):
    """Input contract matching input/EC_xxx.json schema."""
    case_id: str = Field(..., description="Unique case identifier, e.g., 'EC_001'")
    opened_at: str = Field(..., description="ISO 8601 timestamp when ticket was opened")
    customer_request: CustomerRequest
    policy_version: str = Field(default="EC_POLICY_V1", description="Policy version applicable to case")


class OrderSellerResult(BaseModel):
    """Contract delivered by Member 2 (Order & Seller Agent)."""
    order_id: str = Field(..., description="Olist order ID")
    order_status: str = Field(..., description="Order status, e.g., 'delivered', 'canceled', 'unavailable'")
    delivered_carrier_date: Optional[str] = Field(None, description="Timestamp when carrier received order")
    delivered_customer_date: Optional[str] = Field(None, description="Timestamp when customer received order")
    estimated_delivery_date: Optional[str] = Field(None, description="Estimated delivery timestamp")
    item_total_brl: float = Field(0.0, description="Sum of item prices in BRL, rounded to 2 decimal places")
    freight_total_brl: float = Field(0.0, description="Sum of item freight costs in BRL, rounded to 2 decimal places")
    late_seller_ids: List[str] = Field(default_factory=list, description="List of seller IDs who handed off past shipping_limit_date")
    order_ids: List[str] = Field(default_factory=list, description="Entity IDs: order:<order_id>")
    item_ids: List[str] = Field(default_factory=list, description="Entity IDs: <order_id>:<order_item_id>")
    seller_ids: List[str] = Field(default_factory=list, description="Entity IDs: <seller_id>")
    evidence_ids: List[str] = Field(default_factory=list, description="Evidence strings: order:..., item:..., seller:...")


class DeliveryResult(BaseModel):
    """Contract delivered by Delivery Agent."""
    order_id: str = Field(..., description="Olist order ID")
    is_late_delivery: bool = Field(False, description="True if customer delivery date > estimated delivery date")
    is_seller_late: bool = Field(False, description="True if carrier delivery date > shipping_limit_date")
    late_seller_ids: List[str] = Field(default_factory=list, description="List of offending seller IDs")



class PaymentResult(BaseModel):
    """Contract delivered by Member 3 (Payment Agent)."""
    order_id: str = Field(..., description="Olist order ID")
    payment_total_brl: float = Field(0.0, description="Sum of all payment values in BRL, rounded to 2 decimal places")
    payment_count: int = Field(0, description="Number of payment rows for this order")
    payment_matches_order_total: bool = Field(False, description="True if payment_total matches (item_total + freight_total) within 0.10 BRL tolerance")
    is_split_payment: bool = Field(False, description="True if payment_count >= 2")
    payment_ids: List[str] = Field(default_factory=list, description="Entity IDs: <order_id>:<payment_sequential>")
    evidence_ids: List[str] = Field(default_factory=list, description="Evidence strings: payment:<order_id>:<seq>")


class ResponsibleParty(BaseModel):
    """Structure for responsible parties in Root Cause Analysis."""
    party_type: str = Field(..., description="Type of party: 'seller', 'platform', or 'logistics_provider'")
    party_id: str = Field(..., description="Party ID: seller_id, 'OLIST_PLATFORM', or 'LOGISTICS_PROVIDER'")


class PolicyResult(BaseModel):
    """Contract delivered by Member 4 (Delivery & Policy Agent)."""
    primary_issue: str = Field(..., description="Determined primary issue code (one of 6 rules)")
    case_status: str = Field(..., description="'action_required' if refund recommended, else 'no_action'")
    confidence: float = Field(0.95, ge=0.0, le=1.0, description="Assessment confidence score between 0.0 and 1.0")
    root_cause_code: str = Field(..., description="Matching root cause code, e.g., 'SELLER_HANDOFF_AFTER_LIMIT'")
    responsible_parties: List[ResponsibleParty] = Field(default_factory=list, description="List of responsible party objects")
    recommended_refund_brl: float = Field(0.0, description="Calculated refund amount in BRL")
    resolution_actions: List[str] = Field(default_factory=list, description="List of resolution actions, e.g., ['refund_freight']")
    policy_evidence_id: str = Field(..., description="Evidence ID string: policy:<root_cause_code>")


class VerifierResult(BaseModel):
    """Contract delivered by Member 5 (Verifier Agent)."""
    is_valid: bool = Field(..., description="True if output complies 100% with schema and constraint bounds")
    validation_errors: List[str] = Field(default_factory=list, description="List of validation error messages if any")


class Assessment(BaseModel):
    primary_issue: str
    case_status: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class AffectedEntities(BaseModel):
    order_ids: List[str] = Field(default_factory=list, max_length=5)
    item_ids: List[str] = Field(default_factory=list, max_length=5)
    seller_ids: List[str] = Field(default_factory=list, max_length=5)
    payment_ids: List[str] = Field(default_factory=list, max_length=5)


class CauseRank(BaseModel):
    cause_code: str
    rank: int = 1


class RootCauseAnalysis(BaseModel):
    ranked_causes: List[CauseRank] = Field(default_factory=list, max_length=3)
    responsible_parties: List[ResponsibleParty] = Field(default_factory=list, max_length=3)


class FinancialResolution(BaseModel):
    currency: str = Field(default="BRL")
    item_total_brl: float
    freight_total_brl: float
    payment_total_brl: float
    recommended_refund_brl: float


class FinalCaseOutput(BaseModel):
    """Strict final JSON output schema required for EC_xxx.json in output/ directory."""
    case_id: str
    assessment: Assessment
    affected_entities: AffectedEntities
    root_cause_analysis: RootCauseAnalysis
    evidence_ids: List[str] = Field(default_factory=list, max_length=10)
    financial_resolution: FinancialResolution
    resolution_actions: List[str] = Field(default_factory=list, max_length=5)
