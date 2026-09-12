#!/usr/bin/env python3
"""AURA V2-3 Functional Acceptance Test — corrected evaluation field names."""
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8010"

def get(path):
    req = urllib.request.Request(BASE + path, method="GET")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())

def post(path, payload, timeout=90):
    data = json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def check(name, condition, detail):
    print(f"[{'PASS' if condition else 'FAIL'}] {name}: {detail}")
    return condition

results = []
print("\nAURA V2-3 — FUNCTIONAL ACCEPTANCE TEST")
print("=" * 55)

for path in ("/health", "/ready"):
    try:
        p = get(path)
        results.append(check(path, True, json.dumps(p)))
    except Exception as e:
        results.append(check(path, False, str(e)))

try:
    kpis = get("/api/v1/analytics/kpis")
    roots = get("/api/v1/analytics/root-causes")
    insights = get("/api/v1/analytics/insights")
    results.append(check("Analytics APIs",
        isinstance(kpis, dict) and isinstance(roots, list) and isinstance(insights, dict),
        f"kpis={len(kpis)} fields, root_causes={len(roots)}, insights={len(insights)} fields"))
except Exception as e:
    results.append(check("Analytics APIs", False, str(e)))

try:
    flagship = post("/api/v1/cases/resolve", {
        "customer_id": "C10001",
        "message": "My ₹85,000 order was supposed to arrive last week and nobody has helped me."
    })
    ok = (
        flagship.get("customer_id") == "C10001"
        and float(flagship.get("recommended_compensation_inr", 0)) <= 1000
        and flagship.get("approval_required") is False
        and flagship.get("action_status") == "auto_executed"
        and flagship.get("status") == "resolved"
    )
    results.append(check("Flagship autonomous resolution", ok,
        f"case={flagship.get('case_id')}, compensation=₹{flagship.get('recommended_compensation_inr')}, "
        f"approval_required={flagship.get('approval_required')}, action={flagship.get('action_status')}"))

    evidence = flagship.get("evidence", [])
    trace = flagship.get("trace", [])
    results.append(check("Policy/RAG evidence", len(evidence) >= 1,
        f"{len(evidence)} evidence item(s); retrieval_mode={flagship.get('retrieval_mode')}"))
    results.append(check("Agent trace", len(trace) >= 5, f"{len(trace)} trace step(s)"))

    audit = get(f"/api/v1/cases/{flagship['case_id']}/audit")
    events = audit.get("events", [])
    results.append(check("Audit trail", len(events) >= 1,
        f"{len(events)} audit event(s) for {flagship['case_id']}"))
except Exception as e:
    results.append(check("Flagship autonomous resolution", False, str(e)))

try:
    high_value = post("/api/v1/cases/resolve", {
        "customer_id": "C10001",
        "message": "I want a refund of ₹5,000 for this order."
    })
    ok = (
        float(high_value.get("recommended_compensation_inr", 0)) >= 5000
        and high_value.get("approval_required") is True
        and high_value.get("action_status") == "pending_approval"
        and high_value.get("status") == "pending_approval"
    )
    results.append(check("High-value human approval", ok,
        f"case={high_value.get('case_id')}, compensation=₹{high_value.get('recommended_compensation_inr')}, "
        f"approval_required={high_value.get('approval_required')}, action={high_value.get('action_status')}"))
except Exception as e:
    results.append(check("High-value human approval", False, str(e)))

try:
    roi = post("/api/v1/analytics/roi", {
        "annual_interactions": 600000,
        "cost_per_interaction_inr": 180,
        "efficiency_improvement_pct": 20,
        "annual_investment_inr": 6000000,
    })
    ok = (
        round(float(roi["annual_cost_pool_inr"])) == 108000000
        and round(float(roi["annual_benefit_inr"])) == 21600000
        and round(float(roi["simple_roi_pct"])) == 260
        and round(float(roi["payback_months"]), 1) == 3.3
    )
    results.append(check("ROI model", ok,
        f"cost_pool=₹{roi['annual_cost_pool_inr']}, benefit=₹{roi['annual_benefit_inr']}, "
        f"ROI={roi['simple_roi_pct']}%, payback={roi['payback_months']} months"))
except Exception as e:
    results.append(check("ROI model", False, str(e)))

try:
    evaluation = get("/api/v1/evaluation/run")
    accuracy = evaluation.get("classification_accuracy_pct")
    governance = evaluation.get("governance_gate_pass")
    grounding = evaluation.get("policy_grounding_available")
    cases = evaluation.get("benchmark_cases")
    ok = accuracy is not None and governance is not None and grounding is not None and cases == 30
    results.append(check("AI Evaluation", ok,
        f"benchmark_cases={cases}, classification_accuracy={accuracy}%, "
        f"governance_gate={'PASS' if governance else 'REVIEW'}, "
        f"policy_grounding={'AVAILABLE' if grounding else 'UNAVAILABLE'}"))
except Exception as e:
    results.append(check("AI Evaluation", False, str(e)))

print("\n" + "=" * 55)
passed = sum(results)
total = len(results)
print(f"RESULT: {passed}/{total} checks passed")
if passed == total:
    print("AURA V2-3 ACCEPTANCE STATUS: PASS")
    sys.exit(0)
else:
    print("AURA V2-3 ACCEPTANCE STATUS: REVIEW REQUIRED")
    sys.exit(1)
