"""
Hospital routing — capability-aware, deterministic. No LLM.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from .models import WorkingDiagnosis, RoutingDecision

HOSPITALS_FILE = Path(__file__).parent / "data" / "hospitals.json"

CONDITION_TO_CAPABILITIES: dict[str, list[str]] = {
    "cardiac_arrest":       ["cath_lab", "icu", "cardiology"],
    "stemi":                ["cath_lab", "cardiology"],
    "cardiac_event":        ["cath_lab", "cardiology", "icu"],
    "ischemic_stroke":      ["comprehensive_stroke_center", "neurology"],
    "hemorrhagic_stroke":   ["neurosurgery", "comprehensive_stroke_center"],
    "stroke":               ["comprehensive_stroke_center", "neurology"],
    "anaphylaxis":          ["er_basic", "icu"],
    "major_trauma":         ["level_1_trauma", "surgery", "blood_bank"],
    "heat_emergency":       ["er_basic", "icu"],
    "heat_stroke":          ["er_basic", "icu"],
    "pediatric_emergency":  ["pediatric_er", "picu"],
    "unknown_severe":       ["level_1_trauma", "icu", "er_basic"],
    "sensor_error":         ["er_basic", "icu"],
}

TIME_CRITICAL_WINDOWS: dict[str, int] = {
    "ischemic_stroke":  270,
    "stroke":           270,
    "stemi":            90,
    "cardiac_event":    90,
    "anaphylaxis":      15,
    "major_trauma":     60,
}


def load_hospitals() -> list[dict]:
    if not HOSPITALS_FILE.exists():
        return []
    with open(HOSPITALS_FILE) as f:
        return json.load(f)


def calculate_eta(patient_gps: tuple[float, float], hospital: dict) -> int:
    lat1, lon1 = math.radians(patient_gps[0]), math.radians(patient_gps[1])
    lat2 = math.radians(hospital["latitude"])
    lon2 = math.radians(hospital["longitude"])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    dist_km = 6371 * 2 * math.asin(math.sqrt(a))
    return max(1, round((dist_km / 60) * 60))  # 60 km/h ambulance


def score_hospital(hospital: dict, diagnosis: WorkingDiagnosis, patient_gps: tuple[float, float]) -> float:
    required = set(diagnosis.required_capabilities)
    available = set(hospital.get("capabilities", []))
    match_ratio = len(required & available) / max(len(required), 1)
    cap_penalty = (1.0 - match_ratio) * 100

    eta  = calculate_eta(patient_gps, hospital)
    wait = hospital.get("current_er_wait_minutes", 15)

    if diagnosis.top_condition in TIME_CRITICAL_WINDOWS:
        return cap_penalty + (eta * 2) + wait
    return cap_penalty + eta + wait


def route(diagnosis: WorkingDiagnosis, patient_location: tuple[float, float]) -> RoutingDecision:
    hospitals = load_hospitals()
    if not hospitals:
        return RoutingDecision(
            chosen_hospital={}, eta_minutes=0,
            reasoning="No hospitals loaded — check hospitals.json",
            alternatives=[], fallback_triggered=True,
            re_evaluation_triggers=["hospital_data_loaded"],
        )

    condition = diagnosis.top_condition if diagnosis.top_confidence >= 0.6 else "unknown_severe"
    required_caps = CONDITION_TO_CAPABILITIES.get(condition, CONDITION_TO_CAPABILITIES["unknown_severe"])

    routing_diag = WorkingDiagnosis(
        differential=diagnosis.differential,
        top_condition=condition,
        top_confidence=diagnosis.top_confidence,
        required_capabilities=required_caps,
        esi_level=diagnosis.esi_level,
        critical_handoff_facts=diagnosis.critical_handoff_facts,
        conflict_flags=diagnosis.conflict_flags,
        reasoning_trace=diagnosis.reasoning_trace,
    )

    scored = sorted(hospitals, key=lambda h: score_hospital(h, routing_diag, patient_location))
    best = scored[0]
    required_set = set(required_caps)
    best_caps    = set(best.get("capabilities", []))
    fallback     = not required_set.issubset(best_caps)
    eta          = calculate_eta(patient_location, best)

    alternatives = [
        {"hospital": h, "eta_minutes": calculate_eta(patient_location, h)}
        for h in scored[1:3]
    ]

    time_window = TIME_CRITICAL_WINDOWS.get(condition)
    triggers = ["Reassess if patient condition deteriorates en route",
                "Reassess if hospital diverts or capacity changes"]
    if time_window:
        triggers.insert(0, f"Reassess if ETA exceeds {time_window}-min window for {condition}")

    missing = required_set - best_caps
    parts = [
        f"Routing for {condition} (confidence: {diagnosis.top_confidence:.0%})",
        f"Required: {', '.join(required_caps)}",
        f"Selected: {best['name']} — ETA {eta} min, ER wait {best.get('current_er_wait_minutes', '?')} min",
    ]
    if fallback:
        parts.append(f"FALLBACK: missing {missing} — best available match")

    return RoutingDecision(
        chosen_hospital=best,
        eta_minutes=eta,
        reasoning=" | ".join(parts),
        alternatives=alternatives,
        fallback_triggered=fallback,
        re_evaluation_triggers=triggers,
    )
