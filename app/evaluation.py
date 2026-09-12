from __future__ import annotations

from app.agents.orchestrator import classify, resolve
from app.services.data import load_rows


CASES = [
    ("C10001", "My order is late and nobody is helping me.", "delivery_escalation"),
    ("C10002", "Can you tell me the ETA for my shipment?", "delivery_escalation"),
    ("C10003", "I need my money back for this purchase.", "refund_request"),
    ("C10004", "Please cancel my order.", "cancellation"),
    ("C10005", "I was charged incorrectly and need an invoice.", "billing_issue"),
    ("C10001", "The carrier delay is unacceptable and I am frustrated.", "delivery_escalation"),
    ("C10002", "I want a refund, this is a problem.", "refund_request"),
    ("C10003", "Can you cancel this order?", "cancellation"),
    ("C10004", "Why was I charged twice?", "billing_issue"),
    ("C10005", "The delivery is late again.", "delivery_escalation"),
] * 3


def run_evaluation() -> dict:
    rows = []
    correct = 0
    for customer_id, message, expected in CASES:
        predicted, sentiment, priority = classify(message)
        ok = predicted == expected
        correct += int(ok)
        rows.append({"customer_id": customer_id, "expected": expected, "predicted": predicted, "correct": ok})
    classification_accuracy = round(correct / len(CASES) * 100, 2)

    # Governance benchmark: known premium delayed shipment should remain under the autonomous limit.
    demo = resolve("C10001", "My ₹85,000 order is delayed and I need help.")
    governance_pass = demo["recommended_compensation_inr"] <= 1000 and demo["approval_required"] is False

    return {
        "benchmark_cases": len(CASES),
        "classification_accuracy_pct": classification_accuracy,
        "governance_gate_pass": governance_pass,
        "policy_grounding_available": bool(demo.get("evidence")),
        "evaluation_note": "Portfolio benchmark over synthetic cases; not a production accuracy claim.",
        "sample_rows": rows[:12],
    }
