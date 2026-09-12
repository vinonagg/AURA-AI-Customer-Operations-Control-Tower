from __future__ import annotations

import json
from typing import Any

from app.config import settings

SYSTEM = """You are AURA, an enterprise customer-operations decision agent.
Return strict JSON only. Never invent customer, order, shipment, policy, financial or
operational facts. Use only the supplied evidence. You may rewrite the baseline decision
for clarity, but must not increase compensation beyond the evidence/policy constraints.
If evidence is insufficient, lower confidence and recommend human review.
"""


def enrich_with_llm(message: str, evidence: list[str], baseline: dict[str, Any]) -> dict[str, Any]:
    if not settings.openai_api_key or not settings.enable_llm_enrichment:
        return baseline
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            f"Customer message: {message}\n"
            f"Evidence: {json.dumps(evidence)}\n"
            f"Baseline analysis: {json.dumps(baseline)}\n\n"
            "Return JSON with exactly these keys: intent, sentiment, priority, root_cause, "
            "resolution, confidence, compensation_inr. confidence must be between 0 and 1."
        )
        response = client.responses.create(model=settings.openai_model, instructions=SYSTEM, input=prompt)
        data = json.loads(response.output_text)
        allowed = {"intent", "sentiment", "priority", "root_cause", "resolution", "confidence", "compensation_inr"}
        clean = {k: data[k] for k in allowed if k in data}
        clean["confidence"] = max(0.0, min(1.0, float(clean.get("confidence", baseline["confidence"]))))
        clean["compensation_inr"] = max(0.0, float(clean.get("compensation_inr", baseline.get("compensation_inr", 0))))
        return {**baseline, **clean, "llm_enriched": True}
    except Exception as exc:
        return {**baseline, "llm_enriched": False, "llm_error": str(exc)[:180]}
