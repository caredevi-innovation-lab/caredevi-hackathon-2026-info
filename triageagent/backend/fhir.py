"""
FHIR R4 Bundle generator — Synthea-compatible format.
Terminologies: SNOMED CT, LOINC, RxNorm.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from .models import WorkingDiagnosis, SignalBundle

PATIENTS_DIR = Path(__file__).parent / "data" / "patients"

SNOMED_CONDITIONS: dict[str, tuple[str, str]] = {
    "cardiac_arrest":   ("410429000", "Cardiac arrest"),
    "stemi":            ("22298006",  "Myocardial infarction"),
    "cardiac_event":    ("22298006",  "Myocardial infarction"),
    "ischemic_stroke":  ("422504002", "Ischemic stroke"),
    "hemorrhagic_stroke": ("274100004", "Hemorrhagic stroke"),
    "stroke":           ("230690007", "Stroke"),
    "anaphylaxis":      ("39579001",  "Anaphylaxis"),
    "heat_stroke":      ("52072009",  "Heat stroke"),
    "heat_emergency":   ("52072009",  "Heat stroke"),
    "unknown_severe":   ("418799008", "Undifferentiated emergency"),
    "sensor_error":     ("418799008", "Undifferentiated emergency"),
}

LOINC_OBS: dict[str, tuple[str, str, str]] = {
    "heart_rate":       ("8867-4",  "Heart rate",          "beats/minute"),
    "spo2":             ("59408-5", "Oxygen saturation",   "%"),
    "respiratory_rate": ("9279-1",  "Respiratory rate",    "breaths/minute"),
    "body_temperature": ("8310-5",  "Body temperature",    "Cel"),
}


def load_patient_bundle(patient_id: str) -> dict:
    pid = patient_id.lower().replace("-", "_")
    if not pid.startswith("patient_"):
        pid = f"patient_{pid.zfill(3)}"
    fp = PATIENTS_DIR / f"{pid}.json"
    if not fp.exists():
        for f in PATIENTS_DIR.glob("*.json"):
            if patient_id.replace("-", "_") in f.stem:
                fp = f
                break
        else:
            return {}
    with open(fp) as f:
        return json.load(f)


def _resources(bundle: dict, rtype: str) -> list[dict]:
    return [e["resource"] for e in bundle.get("entry", [])
            if e.get("resource", {}).get("resourceType") == rtype]


def get_patient(bundle: dict) -> dict:
    r = _resources(bundle, "Patient")
    return r[0] if r else {}

def get_conditions(bundle: dict)   -> list[dict]: return _resources(bundle, "Condition")
def get_medications(bundle: dict)  -> list[dict]: return _resources(bundle, "MedicationStatement")
def get_allergies(bundle: dict)    -> list[dict]: return _resources(bundle, "AllergyIntolerance")


def generate_handoff_bundle(
    patient_id: str,
    diagnosis: WorkingDiagnosis,
    signal_bundle: SignalBundle,
) -> dict:
    stored = load_patient_bundle(patient_id)
    now = datetime.now(timezone.utc).isoformat()

    snomed_code, snomed_display = SNOMED_CONDITIONS.get(
        diagnosis.top_condition, SNOMED_CONDITIONS["unknown_severe"]
    )

    entries: list[dict] = []

    patient_res = get_patient(stored)
    if patient_res:
        entries.append({"resource": patient_res})

    entries.append({"resource": {
        "resourceType": "Condition",
        "id": f"condition-emergency-{patient_id}",
        "meta": {"lastUpdated": now},
        "subject": {"reference": f"Patient/{patient_id}"},
        "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
        "verificationStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "unconfirmed"}]},
        "code": {"coding": [{"system": "http://snomed.info/sct", "code": snomed_code, "display": snomed_display}]},
        "note": [{"text": "AI-generated preliminary assessment. Not a clinical diagnosis."}],
        "recordedDate": now,
    }})

    obs_map = {
        "heart_rate":       signal_bundle.heart_rate,
        "spo2":             signal_bundle.spo2,
        "respiratory_rate": signal_bundle.respiratory_rate,
    }
    for key, value in obs_map.items():
        if value is not None:
            code, display, unit = LOINC_OBS[key]
            entries.append({"resource": {
                "resourceType": "Observation",
                "id": f"obs-{key}-{patient_id}",
                "meta": {"lastUpdated": now},
                "status": "final",
                "subject": {"reference": f"Patient/{patient_id}"},
                "code": {"coding": [{"system": "http://loinc.org", "code": code, "display": display}]},
                "valueQuantity": {"value": value, "unit": unit},
                "effectiveDateTime": signal_bundle.timestamp.isoformat(),
            }})

    for res in get_conditions(stored) + get_medications(stored) + get_allergies(stored):
        entries.append({"resource": res})

    entries.append({"resource": {
        "resourceType": "Encounter",
        "id": f"encounter-emergency-{patient_id}",
        "meta": {"lastUpdated": now},
        "status": "in-progress",
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "EMER", "display": "emergency"},
        "subject": {"reference": f"Patient/{patient_id}"},
        "period": {"start": signal_bundle.timestamp.isoformat()},
        "location": [{"location": {"display": f"GPS: {signal_bundle.gps[0]:.4f}, {signal_bundle.gps[1]:.4f}"}}],
        "text": {
            "status": "generated",
            "div": (f"<div>AI Triage: {diagnosis.top_condition} "
                    f"(confidence: {diagnosis.top_confidence:.0%}). ESI {diagnosis.esi_level}. "
                    "Disclaimer: AI-generated preliminary assessment. Verify on arrival.</div>"),
        },
    }})

    ts = signal_bundle.timestamp.strftime("%Y%m%dT%H%M%S")
    return {
        "resourceType": "Bundle",
        "id": f"handoff-{patient_id}-{ts}",
        "type": "collection",
        "meta": {"lastUpdated": now},
        "entry": entries,
    }


def format_handoff_summary(
    diagnosis: WorkingDiagnosis,
    signal_bundle: SignalBundle,
    patient_data: dict,
) -> str:
    patient = get_patient(patient_data)
    name = "Unknown"
    if patient and patient.get("name"):
        n = patient["name"][0]
        name = f"{' '.join(n.get('given', []))} {n.get('family', '')}".strip()

    snomed_code, snomed_display = SNOMED_CONDITIONS.get(
        diagnosis.top_condition, SNOMED_CONDITIONS["unknown_severe"]
    )
    lines = [
        "=== FHIR R4 Emergency Handoff Summary ===",
        f"Patient: {name} | Age: {signal_bundle.age} | Blood type: {signal_bundle.blood_type or 'Unknown'}",
        f"Suspected: {diagnosis.top_condition} ({diagnosis.top_confidence:.0%}) | ESI {diagnosis.esi_level}",
        "",
        f"SNOMED CT: {snomed_display} [{snomed_code}]",
        "",
        "LOINC Vitals:",
        f"  HR: {signal_bundle.heart_rate} bpm          [LOINC 8867-4]",
        f"  SpO2: {signal_bundle.spo2}%               [LOINC 59408-5]",
        f"  RR: {signal_bundle.respiratory_rate} br/min         [LOINC 9279-1]",
        "",
        f"Conditions: {', '.join(signal_bundle.conditions) or 'None'}",
        f"Medications: {', '.join(signal_bundle.medications) or 'None'}",
        f"Allergies: {', '.join(signal_bundle.allergies) or 'None'}",
        "",
        "Critical Handoff Facts:",
        *[f"  - {f}" for f in diagnosis.critical_handoff_facts],
    ]
    if diagnosis.conflict_flags:
        lines += ["", "Conflict Flags:", *[f"  ! {f}" for f in diagnosis.conflict_flags]]
    lines.append("\n[DISCLAIMER] AI-generated preliminary assessment. Not a clinical diagnosis. Verify all data on arrival.")
    return "\n".join(lines)


