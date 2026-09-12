from fastapi import APIRouter, HTTPException
from app.schemas import CaseRequest, CaseResponse, ApprovalRequest, ROIRequest, ROIResponse, AskRequest
from app.agents.orchestrator import resolve, approve, reject
from app.db import store
from app.analytics import kpis, root_causes, roi, operational_insights
from app.evaluation import run_evaluation
from app.services.llm import enrich_with_llm

router = APIRouter(prefix="/api/v1")

@router.post("/cases/resolve", response_model=CaseResponse)
def resolve_case(req: CaseRequest):
    return resolve(req.customer_id, req.message)

@router.get("/cases/{case_id}")
def get_case(case_id: str):
    result = store.get_case(case_id)
    if not result:
        raise HTTPException(404, "Case not found")
    result["audit_events"] = store.events(case_id)
    return result

@router.get("/cases/{case_id}/audit")
def get_case_audit(case_id: str):
    if not store.get_case(case_id):
        raise HTTPException(404, "Case not found")
    return {"case_id": case_id, "events": store.events(case_id)}

@router.post("/cases/{case_id}/approve")
def approve_case(case_id: str, req: ApprovalRequest):
    result = approve(case_id, req.approver, req.comment)
    if not result:
        raise HTTPException(404, "Case not found")
    return result

@router.post("/cases/{case_id}/reject")
def reject_case(case_id: str, req: ApprovalRequest):
    result = reject(case_id, req.approver, req.comment)
    if not result:
        raise HTTPException(404, "Case not found")
    return result

@router.get("/analytics/kpis")
def get_kpis():
    return kpis()

@router.get("/analytics/root-causes")
def get_root_causes():
    return root_causes()

@router.get("/analytics/insights")
def get_insights():
    return operational_insights()

@router.post("/analytics/ask")
def ask_aura(req: AskRequest):
    insight = operational_insights()
    roots = root_causes()
    baseline = {
        "answer": (f"The synthetic dataset shows {insight['delayed_shipments']} delayed shipments, with "
                   f"{insight['top_carrier']} representing {insight['top_carrier_share_pct']}% of delayed shipments and "
                   f"{insight['top_hub']} representing {insight['top_hub_share_pct']}% of delayed shipments."),
        "recommendation": insight["recommendation"],
        "confidence": 0.90,
    }
    if not __import__('app.config', fromlist=['settings']).settings.openai_api_key:
        return {**baseline, "mode": "grounded-deterministic"}
    result = enrich_with_llm(req.question, [str(insight), str(roots)], {"intent":"operational_insight", **baseline})
    return {"answer": result.get("resolution", baseline["answer"]), "recommendation": result.get("root_cause", baseline["recommendation"]), "confidence": result.get("confidence", baseline["confidence"]), "mode": "openai"}

@router.post("/analytics/roi", response_model=ROIResponse)
def get_roi(req: ROIRequest):
    return roi(req.annual_interactions, req.cost_per_interaction_inr, req.efficiency_improvement_pct, req.annual_investment_inr)

@router.get("/evaluation/run")
def evaluate():
    return run_evaluation()
