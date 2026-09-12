from app.db.store import init_db
from app.agents.orchestrator import classify, resolve
from app.analytics import roi


def setup_module():
    init_db()


def test_classify_delivery():
    intent, sentiment, priority = classify("My order is late and nobody helped me")
    assert intent == "delivery_escalation"
    assert sentiment == "highly_negative"
    assert priority == "critical"


def test_resolve_demo_case():
    result = resolve("C10001", "My order was supposed to arrive last week and I contacted support twice")
    assert result["case_id"].startswith("AURA-")
    assert result["intent"] == "delivery_escalation"
    assert result["recommended_compensation_inr"] > 0
    assert result["approval_required"] is False
    assert len(result["trace"]) == 8
    assert result["governance"]["decision"] == "autonomous_execution_allowed"


def test_high_value_refund_requires_human():
    result = resolve("C10003", "I want a refund of ₹5,000 because this is unacceptable")
    assert result["intent"] == "refund_request"
    assert result["recommended_compensation_inr"] == 5000
    assert result["approval_required"] is True
    assert result["action_status"] == "pending_approval"


def test_roi():
    r = roi(600000, 180, 20, 6000000)
    assert r["annual_cost_pool_inr"] == 108000000
    assert r["annual_benefit_inr"] == 21600000
    assert r["simple_roi_pct"] == 260
