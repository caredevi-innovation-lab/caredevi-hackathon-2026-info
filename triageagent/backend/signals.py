"""
Sensor fusion and collision detection — cross-validates wearable vs phone sensors.
All deterministic, no LLM.
"""
from __future__ import annotations
from .models import SignalBundle, SignalVerdict


def is_sensor_reading_credible(bundle: SignalBundle) -> tuple[bool, float, str]:
    hr = bundle.heart_rate
    spo2 = bundle.spo2

    if hr == 0 and not bundle.watch_on_wrist:
        return False, 0.10, "HR=0 but watch not on wrist — sensor detachment"
    if hr == 0 and bundle.phone_accelerometer_status == "active":
        return False, 0.20, "HR=0 but phone shows active movement — likely loose watch contact"
    if hr == 0 and bundle.phone_last_interaction_seconds < 300:
        return False, 0.30, f"HR=0 but phone last used {bundle.phone_last_interaction_seconds}s ago — person was active"
    if hr == 0 and bundle.skin_temp is not None and bundle.skin_temp > 35.0:
        return False, 0.40, "HR=0 but skin temp normal (>35°C) — likely loose watch"
    if spo2 is not None and spo2 < 85 and hr is not None and 60 <= hr <= 100:
        return False, 0.35, f"SpO2={spo2}% but HR={hr} normal — contradictory, likely sensor artifact"
    if spo2 is not None and spo2 < 85 and bundle.temperature_celsius < 5:
        return False, 0.40, "SpO2<85 in cold weather (<5°C) — temperature artifact"
    if bundle.fall_detected and bundle.recent_activity == "exercising":
        return True, 0.70, "Fall during exercise — possible artifact, monitoring"

    return True, 0.95, "All sensor readings cross-validated and credible"


def compute_signal_weights(bundle: SignalBundle) -> dict:
    weights = {"sensors": 1.0, "voice": 0.6, "bystander": 0.85, "environment": 0.4, "history": 0.7}
    unresponsive = not bundle.voice_transcript and bundle.movement_status == "still"
    if unresponsive:
        weights["sensors"] = 1.5
        weights["voice"] = 0.0
    if "slurred" in bundle.speech_quality_flags:
        weights["voice"] *= 0.5
    if bundle.spo2 is not None and bundle.spo2 < 90:
        weights["sensors"] = 1.5
        weights["voice"] *= 0.3
    return weights


def detect_conflicts(bundle: SignalBundle) -> list[str]:
    conflicts: list[str] = []
    fine = bundle.voice_transcript and any(
        w in bundle.voice_transcript.lower() for w in ("fine", "ok", "okay", "alright", "good")
    )
    if fine:
        if bundle.spo2 is not None and bundle.spo2 < 92:
            conflicts.append(f"Patient says 'fine' but SpO2={bundle.spo2}% (<92%)")
        if bundle.heart_rate is not None and bundle.heart_rate > 120:
            conflicts.append(f"Patient says 'fine' but HR={bundle.heart_rate} bpm (>120)")
    denies_pain = bundle.voice_transcript and any(
        p in bundle.voice_transcript.lower() for p in ("no chest pain", "no pain", "chest is fine")
    )
    if denies_pain and bundle.ecg_findings in ("st_elevation", "ventricular_fibrillation"):
        conflicts.append(f"Patient denies pain but ECG shows {bundle.ecg_findings}")
    if bundle.fall_detected and bundle.movement_status == "still":
        if bundle.heart_rate is not None and 60 <= bundle.heart_rate <= 100:
            conflicts.append("Fall detected + no movement but HR appears normal — verify sensor contact")
    return conflicts


def get_personalized_thresholds(
    patient_conditions: list[str],
    recent_activity: str,
    temperature: float,
    altitude: int,
) -> dict:
    t = {"hr_low_critical": 40, "hr_high_critical": 150, "spo2_critical": 88,
         "resp_rate_low": 10, "resp_rate_high": 20}
    if any(c in patient_conditions for c in ("athlete", "marathon_runner", "cyclist")):
        t["hr_low_critical"] = 30
    if any(c in patient_conditions for c in ("copd", "chronic_obstructive_pulmonary_disease")):
        t["spo2_critical"] = 82
    if recent_activity in ("running", "exercising"):
        t["hr_high_critical"] = 190
    if altitude > 2000:
        t["spo2_critical"] = 85
    if temperature < 5:
        t["spo2_critical"] = 85
    return t


def collide_and_resolve(bundle: SignalBundle) -> tuple[SignalVerdict, str, int]:
    credible, _, reason = is_sensor_reading_credible(bundle)
    if not credible:
        return SignalVerdict.SENSOR_ERROR, reason, 0

    t = get_personalized_thresholds(
        bundle.conditions, bundle.recent_activity,
        bundle.temperature_celsius, bundle.altitude_meters,
    )

    agreeing: list[str] = []
    if bundle.heart_rate is not None and bundle.heart_rate <= t["hr_low_critical"]:
        agreeing.append("wearable_hr_low")
    if bundle.spo2 is not None and bundle.spo2 < t["spo2_critical"]:
        agreeing.append("wearable_spo2_low")
    if bundle.ecg_findings in ("ventricular_fibrillation", "st_elevation"):
        agreeing.append("wearable_ecg_abnormal")
    if bundle.fall_detected:
        agreeing.append("wearable_fall")
    if bundle.movement_status == "still":
        agreeing.append("wearable_no_movement")
    if bundle.respiratory_rate is not None and bundle.respiratory_rate < t["resp_rate_low"]:
        agreeing.append("wearable_resp_low")
    if bundle.phone_accelerometer_status == "fall_impact":
        agreeing.append("phone_fall_impact")
    if bundle.phone_last_interaction_seconds > 120:
        agreeing.append("phone_no_interaction")
    if bundle.phone_position == "floor":
        agreeing.append("phone_position_floor")

    count = len(agreeing)
    both = any("wearable" in s for s in agreeing) and any("phone" in s for s in agreeing)

    if count >= 3 and both:
        return SignalVerdict.EMERGENCY, f"{count} sensors agree across wearable+phone: {agreeing}", count
    if count >= 1:
        return SignalVerdict.INVESTIGATE, f"{count} sensor(s) flagged: {agreeing}", count
    return SignalVerdict.NORMAL, "All sensors within normal thresholds", 0
