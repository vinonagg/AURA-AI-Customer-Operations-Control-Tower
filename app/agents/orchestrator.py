from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from app.config import settings
from app.db import store
from app.services.data import customer, order_for_customer, shipment_for_order, tickets_for_customer
from app.services.llm import enrich_with_llm
from app.services.rag import PolicyRetriever

retriever = PolicyRetriever()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify(message: str):
    m = message.lower()
    if any(x in m for x in ["delivery", "delivered", "arrive", "shipment", "late", "delay", "eta", "carrier"]):
        intent = "delivery_escalation"
    elif any(x in m for x in ["refund", "money back", "refunds", "reimburse"]):
        intent = "refund_request"
    elif any(x in m for x in ["cancel", "cancellation"]):
        intent = "cancellation"
    elif any(x in m for x in ["payment", "charged", "billing", "invoice"]):
        intent = "billing_issue"
    else:
        intent = "general_support"
    sentiment = (
        "highly_negative" if any(x in m for x in ["angry", "unacceptable", "nobody", "twice", "terrible", "frustrated", "complaint"]) else
        "negative" if any(x in m for x in ["late", "problem", "issue", "delay", "wrong"]) else "neutral"
    )
    priority = "critical" if sentiment == "highly_negative" else "high" if sentiment == "negative" else "medium"
    return intent, sentiment, priority


def _trace(state: dict[str, Any], name: str, status: str, detail: str, evidence: list[str] | None = None):
    state["trace"].append({
        "step": len(state["trace"]) + 1,
        "agent": name,
        "status": status,
        "detail": detail,
        "evidence": evidence or [],
        "timestamp": now(),
    })


def intake_node(state):
    intent, sentiment, priority = classify(state["message"])
    state.update(intent=intent, sentiment=sentiment, priority=priority)
    _trace(state, "Intake Agent", "complete", f"Classified as {intent}; sentiment {sentiment}; priority {priority}.")
    return state


def customer_node(state):
    c = customer(state["customer_id"])
    t = tickets_for_customer(state["customer_id"])
    state["customer"] = c
    state["tickets"] = t
    evidence = []
    if c:
        evidence.append(f"Customer {c['customer_id']}: tier={c['loyalty_tier']}, value=₹{c['customer_value']}")
    evidence.append(f"Previous customer tickets: {len(t)}")
    _trace(state, "Customer Intelligence Agent", "complete", "Customer profile and interaction history retrieved.", evidence)
    return state


def investigation_node(state):
    o = order_for_customer(state["customer_id"])
    s = shipment_for_order(o["order_id"]) if o else None
    state["order"] = o
    state["shipment"] = s
    evidence = []
    if o:
        evidence.append(f"Order {o['order_id']}: value=₹{o['order_value']}, promised={o['promised_date']}, status={o['status']}")
    if s:
        evidence.append(f"Shipment {s['shipment_id']}: carrier={s['carrier']}, hub={s['hub']}, status={s['status']}, reason={s['delay_reason']}")
    detail = "Order and shipment records investigated." if o else "No matching order found; investigation requires human review."
    _trace(state, "Investigation Agent", "complete" if o else "warning", detail, evidence)
    return state


def policy_node(state):
    query = f"{state['intent']} {state['message']} compensation delivery refund escalation"
    hits = retriever.search(query, k=3)
    state["policy_hits"] = hits
    evidence = [f"{p['policy_id']}: {p['policy_text']} (approval={p['approval_required']}, score={p['score']})" for p in hits]
    _trace(state, "Policy Agent", "complete", f"Retrieved {len(hits)} policy records using {retriever.mode} retrieval.", evidence)
    return state


def root_cause_node(state):
    s = state.get("shipment")
    if s and s["status"] == "delayed":
        root = f"Operational delay involving {s['carrier']} at {s['hub']}"
        confidence = 0.93
    elif state.get("order"):
        root = "No confirmed root cause from available evidence."
        confidence = 0.78
    else:
        root = "Insufficient evidence to confirm root cause."
        confidence = 0.62
    state["root_cause"] = root
    state["confidence"] = confidence
    _trace(state, "Root Cause Agent", "complete", root)
    return state


def resolution_node(state):
    c = state.get("customer")
    s = state.get("shipment")
    compensation = 0.0
    resolution = "Provide a clear status update and route the case for human review."
    requested = re.findall(r"(?:₹|inr\s*)\s*([0-9][0-9,]*)", state["message"].lower())
    requested_amount = float(requested[-1].replace(",", "")) if requested else 0.0
    if s and s["status"] == "delayed":
        policy_default = 750.0 if c and c["loyalty_tier"] in ["Gold", "Platinum"] else 500.0
        compensation = requested_amount if requested_amount > 0 and ("compensation" in state["message"].lower() or "refund" in state["message"].lower()) else policy_default
        resolution = f"Escalate shipment with {s['carrier']}, provide updated ETA, and offer ₹{int(compensation)} goodwill credit if policy eligible."
    elif requested_amount > 0 and state["intent"] == "refund_request":
        compensation = requested_amount
        resolution = f"Validate refund eligibility for ₹{int(compensation)} and route for approval if the amount exceeds the autonomous threshold."
    baseline = {
        "intent": state["intent"], "sentiment": state["sentiment"], "priority": state["priority"],
        "root_cause": state["root_cause"], "resolution": resolution, "confidence": state["confidence"],
        "compensation_inr": compensation,
    }
    evidence = []
    evidence.extend([f"Policy: {p['policy_text']}" for p in state.get("policy_hits", [])])
    evidence.extend(state.get("evidence", []))
    enriched = enrich_with_llm(state["message"], evidence, baseline)
    enriched["compensation_inr"] = max(0.0, float(enriched.get("compensation_inr", compensation)))
    # Never let an LLM silently lower/raise the explicit customer request for a material refund.
    if requested_amount > 0 and state["intent"] == "refund_request":
        enriched["compensation_inr"] = requested_amount
    state.update(enriched)
    _trace(state, "Resolution Agent", "complete", state["resolution"])
    return state


def governance_node(state):
    policy_approval = any(str(p.get("approval_required", "")).lower().startswith("yes") for p in state.get("policy_hits", []))
    approval = (
        float(state.get("compensation_inr", 0)) > settings.autonomous_compensation_limit_inr
        or float(state.get("confidence", 0)) < settings.confidence_auto_execute
        or policy_approval and float(state.get("compensation_inr", 0)) > settings.autonomous_compensation_limit_inr
    )
    state["approval_required"] = approval
    state["governance"] = {
        "risk_level": "high" if approval else "low",
        "autonomous_limit_inr": settings.autonomous_compensation_limit_inr,
        "confidence_threshold": settings.confidence_auto_execute,
        "policy_grounded": bool(state.get("policy_hits")),
        "decision": "human_approval_required" if approval else "autonomous_execution_allowed",
    }
    _trace(state, "Governance Agent", "review" if approval else "passed", state["governance"]["decision"])
    return state


def action_node(state):
    state["action_status"] = "pending_approval" if state["approval_required"] else "auto_executed"
    state["status"] = "pending_approval" if state["approval_required"] else "resolved"
    _trace(state, "Action Agent", "queued" if state["approval_required"] else "executed", state["action_status"])
    return state


def resolve(customer_id: str, message: str):
    case_id = "AURA-" + uuid.uuid4().hex[:10].upper()
    state: dict[str, Any] = {
        "case_id": case_id, "customer_id": customer_id, "message": message,
        "trace": [], "evidence": []
    }
    for node in [intake_node, customer_node, investigation_node, policy_node, root_cause_node, resolution_node, governance_node, action_node]:
        node(state)

    c = state.get("customer")
    o = state.get("order")
    s = state.get("shipment")
    evidence = []
    if c: evidence.append(f"Customer {c['customer_id']}: tier={c['loyalty_tier']}, value=₹{c['customer_value']}")
    if o: evidence.append(f"Order {o['order_id']}: value=₹{o['order_value']}, promised={o['promised_date']}, status={o['status']}")
    if s: evidence.append(f"Shipment {s['shipment_id']}: carrier={s['carrier']}, hub={s['hub']}, status={s['status']}, reason={s['delay_reason']}")
    evidence.append(f"Previous customer tickets: {len(state.get('tickets', []))}")
    evidence.extend([f"Policy: {p['policy_text']} (approval={p['approval_required']})" for p in state.get("policy_hits", [])])
    state["evidence"] = evidence

    payload = {
        "case_id": case_id, "status": state["status"], "customer_id": customer_id,
        "intent": state["intent"], "sentiment": state["sentiment"], "priority": state["priority"],
        "confidence": float(state["confidence"]), "root_cause": state["root_cause"], "resolution": state["resolution"],
        "recommended_compensation_inr": float(state.get("compensation_inr", 0)), "approval_required": state["approval_required"],
        "action_status": state["action_status"], "evidence": evidence, "trace": state["trace"],
        "governance": state["governance"], "retrieval_mode": retriever.mode, "llm_enriched": bool(state.get("llm_enriched", False)),
        "customer": c, "order": o, "shipment": s,
    }
    store.save_case(case_id, customer_id, payload)
    for event in [
        ("CASE_CREATED", "Case created and evidence gathered"),
        ("POLICY_RETRIEVED", f"Retrieved {len(state.get('policy_hits', []))} policy records using {retriever.mode}"),
        ("ROOT_CAUSE", state["root_cause"]),
        ("GOVERNANCE", state["governance"]["decision"]),
    ]:
        store.audit(case_id, *event)
    store.action(case_id, "customer_resolution", state["action_status"])
    payload["audit_events"] = store.events(case_id)
    return payload


def approve(case_id, approver, comment=None):
    payload = store.get_case(case_id)
    if not payload:
        return None
    payload["status"] = "resolved"
    payload["action_status"] = "approved_and_executed"
    payload["approval_required"] = False
    payload.setdefault("governance", {})["decision"] = "human_approved"
    store.save_case(case_id, payload["customer_id"], payload)
    store.audit(case_id, "HUMAN_APPROVAL", f"Approved by {approver}. {comment or ''}".strip())
    store.action(case_id, "customer_resolution", "approved_and_executed")
    payload["audit_events"] = store.events(case_id)
    return payload


def reject(case_id, approver, comment=None):
    payload = store.get_case(case_id)
    if not payload:
        return None
    payload["status"] = "escalated"
    payload["action_status"] = "rejected"
    payload["approval_required"] = False
    payload.setdefault("governance", {})["decision"] = "human_rejected"
    store.save_case(case_id, payload["customer_id"], payload)
    store.audit(case_id, "HUMAN_REJECTION", f"Rejected by {approver}. {comment or ''}".strip())
    store.action(case_id, "customer_resolution", "rejected")
    payload["audit_events"] = store.events(case_id)
    return payload
