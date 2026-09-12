from fastapi import FastAPI
from app.db.store import init_db
from app.api.routes import router

app = FastAPI(
    title="AURA — AI Unified Resolution & Analytics",
    version="2.0.0",
    description="Agentic AI customer operations decision platform with policy grounding, governance and operational intelligence.",
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok", "service": "aura-api", "version": "2.0.0"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

app.include_router(router)
