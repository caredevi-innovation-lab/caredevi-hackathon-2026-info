from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="TriageAgent", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_triage_results: dict[str, dict] = {}


@app.on_event("startup")
async def startup() -> None:
    from .ner import load_ner_model
    from .rag import initialize_rag
    from .routing import load_hospitals
    load_ner_model()
    initialize_rag()
    hospitals = load_hospitals()
    print(f"TriageAgent backend ready — {len(hospitals)} hospitals loaded")


# ── request models ────────────────────────────────────────────────────────────

class TriggerRequest(BaseModel):
    patient_id: str
    trigger_type: str                       # "sos_button" | "voice" | "wearable_auto"
    symptoms: Optional[str] = None
    simulated_vitals: Optional[dict] = None


class TriageRequest(BaseModel):
    patient_id: str
    symptoms: str
    signal_bundle: Optional[dict] = None


# ── endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root() -> dict:
    return {"app": "TriageAgent", "status": "running", "version": "0.1.0"}


@app.post("/trigger")
async def trigger(req: TriggerRequest) -> dict:
    from .models import create_mock_signal_bundle
    from .signals import collide_and_resolve

    bundle = create_mock_signal_bundle()
    bundle.patient_id = req.patient_id

    if req.simulated_vitals:
        v = req.simulated_vitals
        for field in ("heart_rate", "spo2", "ecg_findings", "fall_detected",
                      "movement_status", "phone_position", "phone_last_interaction_seconds"):
            if field in v:
                setattr(bundle, field, v[field])

    verdict, reasoning, count = collide_and_resolve(bundle)

    recommendation = {
        "EMERGENCY":    "Initiating emergency protocol — dispatching EMS",
        "INVESTIGATE":  "Unusual readings — 'Are you okay?' check initiated",
        "SENSOR_ERROR": "Sensor inconsistency — check device placement",
        "NORMAL":       "All vitals within normal range — monitoring continues",
    }.get(verdict.value, "Unknown verdict")

    return {
        "verdict":               verdict.value,
        "reasoning":             reasoning,
        "sensor_agreement_count":count,
        "recommendation":        recommendation,
        "trigger_type":          req.trigger_type,
        "patient_id":            req.patient_id,
    }


@app.post("/triage")
async def triage(req: TriageRequest) -> dict:
    from .models import create_mock_signal_bundle
    from .agent import run_triage_agent

    bundle = create_mock_signal_bundle()
    bundle.patient_id = req.patient_id

    if req.signal_bundle:
        for field in ("heart_rate", "spo2", "ecg_findings", "fall_detected",
                      "movement_status", "phone_position", "phone_last_interaction_seconds",
                      "watch_on_wrist", "respiratory_rate"):
            if field in req.signal_bundle:
                setattr(bundle, field, req.signal_bundle[field])

    result = await run_triage_agent(req.patient_id, req.symptoms, bundle)
    result["technologies_used"].update({
        "llm_fallback": "Qwen/Qwen2.5-Coder-32B-Instruct",
        "data":         "Synthea synthetic patients",
        "terminologies":["SNOMED CT", "LOINC", "RxNorm", "ICD-10-CM"],
    })
    _triage_results[req.patient_id] = result
    return result


@app.get("/incoming/{patient_id}")
async def incoming(patient_id: str) -> dict:
    result = _triage_results.get(patient_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"No triage result found for patient {patient_id}")
    return result


@app.get("/incoming")
async def all_incoming() -> dict:
    return {
        "patients": list(_triage_results.keys()),
        "count":    len(_triage_results),
        "results":  _triage_results,
    }


@app.get("/tech-stack")
async def tech_stack() -> dict:
    return {
        "name":      "TriageAgent",
        "hackathon": "AI Healthcare Innovation Hackathon 2026",
        "tracks":    ["AI Patient Triage", "Health Data & Interoperability", "AI-Powered Care Coordination"],
        "technologies": {
            "llm": {
                "primary":  "aaditya/Llama3-OpenBioLLM-70B",
                "fallback": "Qwen/Qwen2.5-Coder-32B-Instruct",
                "source":   "HuggingFace Inference API (OpenAI-compatible endpoint)",
            },
            "ner": {
                "model":       "scispaCy en_core_sci_md",
                "alternative": "johnsnowlabs/JSL-MedS-NER-q16_v2",
                "terminologies": "SNOMED CT mapping",
            },
            "rag": {
                "vector_store": "ChromaDB",
                "embeddings":   "sentence-transformers/all-MiniLM-L6-v2",
                "framework":    "LangChain",
                "protocols":    6,
            },
            "fhir": {
                "version":       "R4",
                "data":          "Synthea synthetic patients",
                "terminologies": ["SNOMED CT", "LOINC", "RxNorm", "ICD-10-CM"],
            },
            "backend": "FastAPI (Python 3.10+)",
            "deterministic_layers": [
                "Sensor fusion and collision detection (signals.py)",
                "Emergency detection rules (detection.py)",
                "Hospital capability routing (routing.py)",
                "ESI severity scoring (detection.py)",
            ],
        },
    }
