from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class SignalVerdict(str, Enum):
    EMERGENCY = "EMERGENCY"
    INVESTIGATE = "INVESTIGATE"
    SENSOR_ERROR = "SENSOR_ERROR"
    NORMAL = "NORMAL"


@dataclass
class SignalBundle:
    # Identity / timing
    timestamp: datetime
    patient_id: str

    # FHIR history
    age: int
    conditions: list[str]
    medications: list[str]
    allergies: list[str]
    blood_type: Optional[str]

    # Wearable sensors
    heart_rate: Optional[int]
    spo2: Optional[int]
    ecg_findings: Optional[str]          # "normal" | "afib" | "st_elevation" | "ventricular_fibrillation"
    fall_detected: bool
    movement_status: str                  # "active" | "still" | "micro_movements"
    watch_on_wrist: bool
    skin_temp: Optional[float]
    respiratory_rate: Optional[int]

    # Phone sensors
    phone_accelerometer_status: str       # "active" | "still" | "fall_impact"
    phone_last_interaction_seconds: int
    phone_position: str                   # "hand" | "pocket" | "table" | "floor"

    # Patient voice
    voice_transcript: Optional[str]
    speech_quality_flags: list[str]       # e.g. ["slurred", "truncated"]
    extracted_symptoms: list[str]

    # Environment
    location_type: str
    gps: tuple[float, float]
    altitude_meters: int
    time_of_day: str
    temperature_celsius: float
    humidity_percent: int
    weather_condition: str

    # Recent activity
    recent_activity: str                  # "resting" | "sleeping" | "walking" | "running" | "driving" | "exercising"


@dataclass
class WorkingDiagnosis:
    differential: list[tuple[str, float]]   # [(condition, confidence), ...]
    top_condition: str
    top_confidence: float
    required_capabilities: list[str]
    esi_level: int                           # 1 (most critical) – 5
    critical_handoff_facts: list[str]
    conflict_flags: list[str]
    reasoning_trace: str


@dataclass
class RoutingDecision:
    chosen_hospital: dict
    eta_minutes: int
    reasoning: str
    alternatives: list[dict]
    fallback_triggered: bool
    re_evaluation_triggers: list[str]


def create_mock_signal_bundle() -> SignalBundle:
    """Return a realistic SignalBundle for a 62-year-old male in cardiac arrest at home."""
    return SignalBundle(
        timestamp=datetime.now(timezone.utc),
        patient_id="patient-001",

        # FHIR history
        age=62,
        conditions=["hypertension", "type_2_diabetes", "coronary_artery_disease"],
        medications=["metoprolol", "lisinopril", "aspirin", "atorvastatin"],
        allergies=["penicillin"],
        blood_type="O+",

        # Wearable — VF arrest: HR flatline, SpO2 crashing
        heart_rate=0,
        spo2=72,
        ecg_findings="ventricular_fibrillation",
        fall_detected=True,
        movement_status="still",
        watch_on_wrist=True,
        skin_temp=34.8,  # slightly cool — consistent with arrest
        respiratory_rate=0,

        # Phone fell with patient, no interaction for 5+ minutes
        phone_accelerometer_status="fall_impact",
        phone_last_interaction_seconds=310,
        phone_position="floor",

        # Voice — no response
        voice_transcript=None,
        speech_quality_flags=[],
        extracted_symptoms=["unresponsive", "no_pulse"],

        # Environment — home, evening
        location_type="residential",
        gps=(29.8833, -97.9414),  # San Marcos, TX
        altitude_meters=52,
        time_of_day="evening",
        temperature_celsius=19.5,
        humidity_percent=58,
        weather_condition="clear",

        # Activity — was resting before arrest
        recent_activity="resting",
    )
