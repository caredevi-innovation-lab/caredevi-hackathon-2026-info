"""
main.py — FastAPI entry point for TriageAgent.

Endpoints (all return {"status": "not implemented"} until wired up):
    POST /trigger                — wearable signals trigger event
    POST /triage                 — run full triage + routing flow
    GET  /incoming/{patient_id}  — fetch incoming patient data
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TriageAgent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "service": "TriageAgent API"}


@app.post("/trigger")
async def trigger() -> dict[str, str]:
    # TODO: accept wearable signal payload, run detection, dispatch alerts
    return {"status": "not implemented"}


@app.post("/triage")
async def triage() -> dict[str, str]:
    # TODO: run full agent + routing flow, return RoutingDecision + FHIR Bundle
    return {"status": "not implemented"}


@app.get("/incoming/{patient_id}")
async def incoming(patient_id: str) -> dict[str, str]:
    # TODO: fetch patient data from FHIR server or local store
    return {"status": "not implemented"}
