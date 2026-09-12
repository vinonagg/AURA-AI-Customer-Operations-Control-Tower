# AURA Architecture

## Runtime components

- **FastAPI**: API and orchestration boundary.
- **Streamlit**: executive and operations UI.
- **SQLite**: local portfolio/demo audit store.
- **CSV data**: synthetic customer, order, shipment, ticket and policy records.
- **Semantic RAG**: OpenAI `text-embedding-3-small` with local TF-IDF fallback.
- **LLM enrichment**: configurable OpenAI Responses API model.

## Decision sequence

1. Intake — classify intent, sentiment and priority.
2. Customer intelligence — retrieve profile and interaction history.
3. Investigation — retrieve order and shipment evidence.
4. Policy — retrieve applicable policy evidence.
5. Root cause — identify the most supported operational cause.
6. Resolution — produce a grounded recommendation.
7. Governance — apply policy, confidence and compensation thresholds.
8. Action — auto-execute or require human approval.
9. Audit — record decision and action events.

## Design principle

AURA separates **recommendation** from **execution**. The model can propose a resolution, but the governance layer decides whether autonomous execution is permitted.
