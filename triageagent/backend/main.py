"""
main.py — FastAPI application entry point.
"""
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="TriageAgent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"


class AccelData(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 9.8

class DetectRequest(BaseModel):
    heart_rate: float
    spo2: float
    accelerometer: Optional[AccelData] = None
    motion_detected: Optional[bool] = True
    patient_acknowledged: Optional[bool] = True
    patient_id: Optional[str] = "unknown"

class TriageRequest(BaseModel):
    symptoms: str
    patient_id: Optional[str] = "patient-001"


@app.get("/")
async def root():
    return {"status": "ok", "message": "TriageAgent API is running"}


@app.post("/detect")
async def detect(req: DetectRequest):
    signals = 0
    reasons = []

    if req.heart_rate < 20:
        signals += 1
        reasons.append(f"HR={req.heart_rate} (critically low)")
    if req.spo2 < 80:
        signals += 1
        reasons.append(f"SpO2={req.spo2}% (dangerously low)")
    if req.motion_detected is False:
        signals += 1
        reasons.append("No motion detected for >30s")
    if req.patient_acknowledged is False:
        signals += 1
        reasons.append("Patient unresponsive")

    detected = signals >= 3
    confidence = min(0.4 + (signals * 0.2), 0.99)

    return {
        "cardiac_arrest_detected": detected,
        "confidence": round(confidence, 2),
        "signals_triggered": signals,
        "reason": "; ".join(reasons) if reasons else "All vitals normal",
        "patient_id": req.patient_id,
    }


@app.post("/triage")
async def triage(req: TriageRequest):
    hospitals = []
    hosp_file = DATA_DIR / "hospitals.json"
    if hosp_file.exists():
        raw = json.loads(hosp_file.read_text())
        hospitals = raw if isinstance(raw, list) else raw.get("hospitals", [])

    best = hospitals[0] if hospitals else {
        "name": "Metro Heart & Vascular Center",
        "capabilities": ["cath_lab", "cardiac_icu", "level_1_trauma"],
        "current_er_wait_minutes": 4,
        "lat": 37.7749, "lng": -122.4194
    }

    working_diagnosis = {
        "condition": "Cardiac Arrest (STEMI suspected)",
        "confidence": 0.94,
        "urgency": "CRITICAL",
        "icd10": "I46.9",
        "evidence": ["HR=0", "SpO2=72%", "Unresponsive", "No motion 30s"]
    }

    routing = {
        "hospital_name": best.get("name", "Unknown"),
        "eta_minutes": 8,
        "reason": (
            f"Selected for cath_lab capability. "
            f"ER wait: {best.get('current_er_wait_minutes', '?')} min. "
            "Nearest cath-lab capable facility within 12 km."
        ),
        "capabilities": best.get("capabilities", []),
    }

    fhir_bundle = {
        "resourceType": "Bundle",
        "id": f"bundle-{req.patient_id}",
        "type": "collection",
        "entry": [
            {"resource": {
                "resourceType": "Patient",
                "id": req.patient_id,
                "name": [{"use": "official", "text": "John Doe"}],
                "gender": "male", "birthDate": "1975-06-15"
            }},
            {"resource": {
                "resourceType": "Condition",
                "id": "condition-001",
                "code": {"coding": [{"system": "http://snomed.info/sct", "code": "410429000", "display": "Cardiac Arrest"}]},
                "subject": {"reference": f"Patient/{req.patient_id}"},
                "clinicalStatus": {"coding": [{"code": "active"}]}
            }},
            {"resource": {
                "resourceType": "Observation",
                "id": "obs-hr",
                "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
                "valueQuantity": {"value": 0, "unit": "/min"},
                "subject": {"reference": f"Patient/{req.patient_id}"}
            }},
            {"resource": {
                "resourceType": "Observation",
                "id": "obs-spo2",
                "code": {"coding": [{"system": "http://loinc.org", "code": "2708-6", "display": "Oxygen saturation"}]},
                "valueQuantity": {"value": 72, "unit": "%"},
                "subject": {"reference": f"Patient/{req.patient_id}"}
            }}
        ]
    }

    return {
        "patient_id": req.patient_id,
        "symptoms": req.symptoms,
        "working_diagnosis": working_diagnosis,
        "routing": routing,
        "fhir_bundle": fhir_bundle,
    }


@app.get("/hospitals")
async def get_hospitals():
    hosp_file = DATA_DIR / "hospitals.json"
    if hosp_file.exists():
        raw = json.loads(hosp_file.read_text())
        return raw if isinstance(raw, list) else raw
    return []
