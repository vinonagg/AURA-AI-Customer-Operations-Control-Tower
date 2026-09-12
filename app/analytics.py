from collections import Counter
from app.services.data import load_rows


def kpis():
    tickets = load_rows("tickets.csv")
    total = len(tickets) or 1
    resolved = sum(1 for x in tickets if x["status"] == "resolved")
    escalated = sum(1 for x in tickets if x["priority"] in ["high", "critical"])
    return {
        "demo_ticket_volume": len(tickets),
        "demo_resolution_rate_pct": round(resolved / total * 100, 2),
        "demo_high_priority_rate_pct": round(escalated / total * 100, 2),
        "enterprise_annual_interactions": 600000,
        "enterprise_cost_per_interaction_inr": 180,
        "enterprise_annual_cost_pool_inr": 108000000,
        "ai_automation_hypothesis_pct": 35,
        "target_aht_reduction_pct": 25,
        "target_fcr_pct": 80,
        "modeling_note": "Enterprise figures are scenario assumptions; demo counts are synthetic.",
    }


def root_causes():
    shipments = load_rows("shipments.csv")
    counts = Counter((s["delay_reason"] or "No delay") for s in shipments)
    return sorted([{"root_cause": k, "cases": v} for k, v in counts.items()], key=lambda x: x["cases"], reverse=True)


def operational_insights():
    shipments = load_rows("shipments.csv")
    delayed = [s for s in shipments if s["status"] == "delayed"]
    carrier = Counter(s["carrier"] for s in delayed)
    hubs = Counter(s["hub"] for s in delayed)
    return {
        "delayed_shipments": len(delayed),
        "top_carrier": carrier.most_common(1)[0][0] if carrier else None,
        "top_carrier_share_pct": round(carrier.most_common(1)[0][1] / len(delayed) * 100, 1) if delayed else 0,
        "top_hub": hubs.most_common(1)[0][0] if hubs else None,
        "top_hub_share_pct": round(hubs.most_common(1)[0][1] / len(delayed) * 100, 1) if delayed else 0,
        "recommendation": "Review carrier and hub-level SLA performance; prioritize open delayed shipments for proactive outreach.",
    }


def roi(interactions, cost, efficiency, investment):
    pool = interactions * cost
    benefit = pool * (efficiency / 100)
    simple_roi = (benefit - investment) / investment * 100
    payback = investment / benefit * 12 if benefit else 0
    return {"annual_cost_pool_inr": round(pool, 2), "annual_benefit_inr": round(benefit, 2), "simple_roi_pct": round(simple_roi, 2), "payback_months": round(payback, 2)}
