from typing import Any, Optional
from pydantic import BaseModel, Field


class CaseRequest(BaseModel):
    customer_id: str = Field(min_length=3, max_length=64)
    message: str = Field(min_length=5, max_length=5000)


class CaseResponse(BaseModel):
    case_id: str
    status: str
    customer_id: str
    intent: str
    sentiment: str
    priority: str
    confidence: float
    root_cause: str
    resolution: str
    recommended_compensation_inr: float
    approval_required: bool
    action_status: str
    evidence: list[str]
    audit_events: list[dict]
    trace: list[dict] = []
    governance: dict[str, Any] = {}
    retrieval_mode: str = "tfidf-fallback"
    llm_enriched: bool = False


class ApprovalRequest(BaseModel):
    approver: str = Field(min_length=2, max_length=128)
    comment: Optional[str] = Field(default=None, max_length=1000)


class ROIRequest(BaseModel):
    annual_interactions: int = Field(default=600000, gt=0)
    cost_per_interaction_inr: float = Field(default=180, gt=0)
    efficiency_improvement_pct: float = Field(default=20, ge=0, le=100)
    annual_investment_inr: float = Field(default=6000000, gt=0)


class ROIResponse(BaseModel):
    annual_cost_pool_inr: float
    annual_benefit_inr: float
    simple_roi_pct: float
    payback_months: float

class AskRequest(BaseModel):
    question: str = Field(min_length=5, max_length=1000)
