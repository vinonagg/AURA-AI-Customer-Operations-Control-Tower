# AURA — AI Unified Resolution & Analytics

## Enterprise AI Customer Operations Control Tower

AURA is a portfolio-grade, end-to-end GenAI decision-intelligence platform for fictional enterprise **NexaCommerce**. It demonstrates how governed agentic AI can investigate customer issues, combine customer/order/shipment evidence, retrieve policy guidance, identify root cause, recommend a resolution, apply a governance gate, execute low-risk actions, route higher-risk decisions for human approval, and preserve an audit trail.

> **Portfolio/demo project:** NexaCommerce data is synthetic and the business economics are scenario assumptions. The evaluation benchmark is synthetic and must not be represented as production model performance.

## Product proposition

**From Issues to Insights. From Support to Strategic Impact.**

AURA is designed as an **AI operations control tower**, not a chatbot. The product combines case-level resolution with executive visibility into governance, root causes, operational signals, evaluation and modeled value.

## What AURA demonstrates

- **Agentic orchestration:** Intake → Customer Intelligence → Investigation → Policy → Root Cause → Resolution → Governance → Action
- **Policy-grounded retrieval:** OpenAI embeddings (`text-embedding-3-small`) when enabled, with deterministic TF-IDF fallback
- **Governed actioning:** configurable autonomous compensation limit and confidence threshold
- **Human-in-the-loop:** higher-value decisions are routed to approval instead of being silently executed
- **Explainability:** evidence, agent trace, governance decision and audit events are exposed in the UI/API
- **Operational intelligence:** root-cause concentration and natural-language executive insights
- **Value modeling:** annual cost pool, modeled benefit, simple ROI and payback
- **AI evaluation:** 30-case synthetic benchmark with governance sanity checks
- **API + executive UI:** FastAPI backend with a Streamlit executive control tower
- **Auditability:** SQLite audit trail for portfolio/demo use

## Solution architecture

```text
Customer Case
    │
    ▼
AURA Agentic Orchestrator
    ├── Intake Agent
    ├── Customer Intelligence Agent ──► Customer / Ticket data
    ├── Investigation Agent ──────────► Order / Shipment data
    ├── Policy Agent ─────────────────► Policy corpus / RAG
    ├── Root Cause Agent
    ├── Resolution Agent ─────────────► Optional LLM enrichment
    ├── Governance Agent ─────────────► Policy + threshold + confidence
    └── Action Agent ─────────────────► Auto execution / Human approval
                     │
                     ▼
                 Audit Trail
                     │
                     ▼
          Executive Control Tower
```

## Current acceptance evidence

The final V2-3 functional acceptance run completed **10/10 checks**:

| Capability | Result |
|---|---|
| API health/readiness | PASS |
| Analytics APIs | PASS |
| ₹750 autonomous resolution | PASS |
| Policy/RAG evidence | PASS |
| 8-step agent trace | PASS |
| Audit trail | PASS |
| ₹5,000 human approval | PASS |
| ROI model | PASS |
| 30-case AI evaluation | PASS |
| Governance gate | PASS |

The reported synthetic evaluation result was **100.0% classification accuracy** with the governance gate passing. Treat this strictly as a portfolio benchmark, not as production performance.

## Flagship demo journeys

### 1. Low-risk autonomous resolution

Customer `C10001` has a delayed high-value order. AURA investigates the customer/order/shipment context, retrieves policy evidence, identifies the operational issue, recommends a **₹750 goodwill credit**, passes the governance gate and records an autonomous action.

### 2. High-value human approval

A customer requests a **₹5,000 refund**. AURA retrieves the relevant policy, recognizes that the amount exceeds the autonomous threshold, and routes the case to **pending approval** instead of executing it automatically.

### 3. Executive value case

The default portfolio scenario models:

- 600,000 annual interactions
- ₹180 cost per interaction
- 20% modeled efficiency improvement
- ₹6,000,000 annual AI program investment
- ₹108,000,000 annual cost pool
- ₹21,600,000 modeled annual benefit
- 260% simple ROI
- 3.33-month payback

These are **scenario assumptions**, not realized business results.

## Run locally

### Prerequisites

Python 3.13 is the validated project environment used for the acceptance run.

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. python scripts/seed_demo.py
```

### Start the API

Terminal 1:

```bash
PYTHONPATH=. python -m uvicorn app.main:app --reload --port 8010
```

### Start the control tower

Terminal 2:

```bash
AURA_API_URL=http://127.0.0.1:8010 PYTHONPATH=. python -m streamlit run streamlit_app/app.py --server.port 8501
```

Open:

- API docs: `http://127.0.0.1:8010/docs`
- AURA Control Tower: `http://localhost:8501`

## Run acceptance tests

With the API running:

```bash
python scripts/run_acceptance.py
```

Expected release status:

```text
AURA V2-3 ACCEPTANCE STATUS: PASS
```

## OpenAI / deterministic demo modes

Set `OPENAI_API_KEY` in `.env` to enable the OpenAI-backed enrichment path and semantic policy embeddings when enabled. Without a key, AURA remains runnable using deterministic fallback retrieval.

Never commit `.env` or a real API key. `.env.example` intentionally contains an empty `OPENAI_API_KEY` value.

## Repository structure

```text
.
├── app/
│   ├── agents/             # Agentic orchestration and reasoning flow
│   ├── api/                # FastAPI routes
│   ├── db/                 # Audit persistence
│   ├── services/           # Retrieval / LLM services
│   ├── analytics.py
│   ├── evaluation.py
│   ├── config.py
│   ├── main.py
│   └── schemas.py
├── config/
├── data/                   # Synthetic demo datasets
├── docs/                   # Product, architecture, governance and business docs
├── scripts/
│   ├── seed_demo.py
│   ├── smoke.py
│   └── aura_v2_3_acceptance_test.py
├── streamlit_app/
│   └── app.py              # Executive Control Tower UI
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## Security and production hardening

The current implementation is a portfolio/demo system. Before using real customer data or money-moving workflows, harden it with:

- SSO/OIDC and RBAC
- Managed database and secrets manager
- PII detection/redaction and retention controls
- Structured logs, traces and metrics
- Prompt/model/version governance
- Security and privacy review
- Rate limiting and abuse controls
- Production evaluation/monitoring
- Enterprise CRM/OMS/TMS integrations
- Human approval queues with SLA controls
- Transaction controls, idempotency and rollback patterns

See `SECURITY.md` and `config/production-checklist.md`.

## Portfolio positioning

> **Built an agentic AI customer-operations control tower that grounds resolutions in enterprise policy, investigates customer/order/shipment evidence, automates low-risk actions, escalates higher-risk decisions to humans, exposes an auditable decision trail, and quantifies the operational value opportunity.**

The project is intentionally positioned around **AI program delivery, governance, operational transformation and measurable business impact**, with the technical implementation supporting the leadership story.

## License / usage

Portfolio demonstration project for fictional NexaCommerce scenarios. Do not upload real customer data, secrets or production credentials.
