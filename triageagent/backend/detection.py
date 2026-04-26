"""
Emergency detection rules — pure deterministic, no LLM.
"""
from __future__ import annotations
from .models import SignalBundle, SignalVerdict
from .signals import collide_and_resolve, is_sensor_reading_credible


def detect_cardiac_arrest(bundle: SignalBundle) -> tuple[bool, float, str]:
    credible, _, _ = is_sensor_reading_credible(bundle)
    if not credible:
        return False, 0.0, "Sensor data not credible — skipping cardiac arrest detection"

    if bundle.ecg_findings == "ventricular_fibrillation" and bundle.watch_on_wrist:
        return True, 0.95, "VF on ECG confirmed with watch on wrist"
    if (bundle.heart_rate is not None and bundle.heart_rate < 30
            and bundle.fall_detected and bundle.movement_status == "still"
            and bundle.watch_on_wrist):
        return True, 0.80, "HR<30 + fall detected + no movement + watch confirmed"
    if (bundle.heart_rate == 0 and bundle.movement_status == "still"
            and bundle.watch_on_wrist and bundle.phone_last_interaction_seconds > 120):
        return True, 0.75, "HR=0 + still + watch on wrist + phone inactive >2min"

    return False, 0.0, "Cardiac arrest criteria not met"


def detect_stroke(bundle: SignalBundle) -> tuple[bool, float, str]:
    combined = " ".join(bundle.extracted_symptoms).lower()
    if bundle.voice_transcript:
        combined += " " + bundle.voice_transcript.lower()

    slurred   = "slurred" in bundle.speech_quality_flags
    arm_weak  = any(w in combined for w in ("arm weakness", "weak arm", "arm numb", "arm pain"))
    face      = any(w in combined for w in ("face", "facial", "drooping"))
    sudden_ha = any(w in combined for w in ("sudden headache", "worst headache", "thunderclap"))
    confusion = "confusion" in bundle.extracted_symptoms or "aphasic" in bundle.speech_quality_flags

    if slurred and arm_weak and face:
        return True, 0.85, "FAST positive: slurred speech + arm weakness + facial involvement"
    if sudden_ha and confusion:
        return True, 0.70, "Possible hemorrhagic stroke: sudden severe headache + confusion"
    if "aphasic" in bundle.speech_quality_flags:
        return True, 0.75, "Aphasia detected — stroke sign"

    return False, 0.0, "Stroke criteria not met"


def detect_cardiac_event(bundle: SignalBundle) -> tuple[bool, float, str]:
    combined = " ".join(bundle.extracted_symptoms).lower()
    if bundle.voice_transcript:
        combined += " " + bundle.voice_transcript.lower()

    if bundle.ecg_findings == "st_elevation":
        return True, 0.90, "ST elevation on ECG — STEMI pattern"

    chest_pain = any(w in combined for w in ("chest pain", "chest tightness", "pressure", "crushing"))
    radiation  = any(w in combined for w in ("arm", "jaw", "back", "radiating"))
    sweating   = any(w in combined for w in ("sweating", "diaphoresis"))
    nausea     = "nausea" in combined
    cardiac_hx = any(c in bundle.conditions for c in
                     ("myocardial_infarction", "coronary_artery_disease", "prior_mi", "cad"))

    if chest_pain and radiation:
        return True, 0.75, "Classic MI presentation: chest pain + radiation"
    if chest_pain and sweating and nausea and cardiac_hx:
        return True, 0.80, "MI with risk factors: chest pain + diaphoresis + nausea + cardiac history"

    return False, 0.0, "Cardiac event criteria not met"


def detect_anaphylaxis(bundle: SignalBundle) -> tuple[bool, float, str]:
    combined = " ".join(bundle.extracted_symptoms).lower()
    if bundle.voice_transcript:
        combined += " " + bundle.voice_transcript.lower()

    airway = any(w in combined for w in ("throat swelling", "throat tightening", "difficulty breathing", "stridor"))
    skin   = any(w in combined for w in ("hives", "rash", "urticaria", "flushing"))

    if airway and skin and bundle.allergies:
        return True, 0.85, "Anaphylaxis: airway compromise + skin involvement + known allergen history"
    if (bundle.spo2 is not None and bundle.spo2 < 90
            and bundle.heart_rate is not None and bundle.heart_rate > 100 and skin):
        return True, 0.70, "Possible anaphylaxis: SpO2 drop + tachycardia + skin symptoms"

    return False, 0.0, "Anaphylaxis criteria not met"


def detect_heat_emergency(bundle: SignalBundle) -> tuple[bool, float, str]:
    combined = " ".join(bundle.extracted_symptoms).lower()
    if bundle.voice_transcript:
        combined += " " + bundle.voice_transcript.lower()

    outdoor   = bundle.location_type in ("outdoor", "park", "field", "construction")
    confusion = any(w in combined for w in ("confusion", "dizzy", "dizziness", "disoriented"))
    elderly   = bundle.age >= 65

    if (bundle.temperature_celsius > 40
            and bundle.heart_rate is not None and bundle.heart_rate > 100 and outdoor):
        return True, 0.75, "Heat stroke: ambient temp >40°C + tachycardia + outdoors"
    if bundle.temperature_celsius > 38 and confusion and elderly:
        return True, 0.70, "Heat emergency: elevated temp + confusion + elderly patient"

    return False, 0.0, "Heat emergency criteria not met"


def run_all_detections(bundle: SignalBundle) -> list[tuple[str, bool, float, str]]:
    verdict, _, _ = collide_and_resolve(bundle)
    if verdict == SignalVerdict.SENSOR_ERROR:
        return [("sensor_error", True, 1.0, "Sensor data not credible — detection skipped")]

    results = [
        ("cardiac_arrest",  *detect_cardiac_arrest(bundle)),
        ("stroke",          *detect_stroke(bundle)),
        ("cardiac_event",   *detect_cardiac_event(bundle)),
        ("anaphylaxis",     *detect_anaphylaxis(bundle)),
        ("heat_emergency",  *detect_heat_emergency(bundle)),
    ]
    return sorted(results, key=lambda x: x[2], reverse=True)


def score_esi(detections: list[tuple], bundle: SignalBundle) -> int:
    detected = {name: (flag, conf) for name, flag, conf, _ in detections if flag}

    if "cardiac_arrest" in detected:
        return 1
    if bundle.ecg_findings == "ventricular_fibrillation":
        return 1
    if "cardiac_event" in detected and detected["cardiac_event"][1] >= 0.85:
        return 1
    if "stroke" in detected:
        return 1
    if "anaphylaxis" in detected:
        return 1
    if "cardiac_event" in detected:
        return 2
    if any(conf >= 0.70 for _, conf in detected.values()):
        return 2
    if "heat_emergency" in detected:
        return 3
    if bundle.heart_rate is not None and bundle.heart_rate > 100:
        return 3
    return 3
