"""
Triage agent — HuggingFace Llama3-OpenBioLLM-70B via OpenAI-compatible endpoint.
Sequential pipeline: all deterministic steps first, LLM only for synthesis.
Fallback: Qwen/Qwen2.5-Coder-32B-Instruct, then fully deterministic.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from .models import SignalBundle, WorkingDiagnosis
from .ner import extract_clinical_entities, detect_speech_quality
from .rag import retrieve_relevant_protocols, build_grounded_prompt
from .signals import collide_and_resolve, detect_conflicts
from .detection import run_all_detections, score_esi
from .routing import route
from .fhir import load_patient_bundle, generate_handoff_bundle, format_handoff_summary

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

DISCLAIMER = "This is AI-generated preliminary information. Not a clinical diagnosis."
HF_ROUTER_BASE_URL = "https://router.huggingface.co/v1"
HF_PRIMARY_MODEL = os.getenv("HF_MODEL", "aaditya/Llama3-OpenBioLLM-70B")
HF_FALLBACK_MODELS = ("Qwen/Qwen2.5-Coder-32B-Instruct",)

_SYSTEM_PROMPT = (
    "You are a clinical decision SUPPORT assistant for emergency triage.\n"
    "Answer ONLY based on the provided patient data, sensor readings, and clinical protocols below.\n"
    "If the answer is not clearly supported, say 'I don't have enough information to assess this.'\n\n"
    "Rules:\n"
    "- Provide confidence scores (0-1) for every assessment with supporting evidence\n"
    "- Use language like 'possible', 'suspected', 'consistent with' — never definitive\n"
    "- Flag conflicts between data sources\n"
    "- Reference specific protocol guidelines\n"
    "- Never invent data not in the provided context\n"
    "- Respond ONLY in valid JSON format\n"
    f"- End with the disclaimer: '{DISCLAIMER}'"
)

_JSON_SCHEMA = (
    '\nRespond ONLY with valid JSON matching this schema:\n'
    '{\n'
    '  "suspected_conditions": [{"condition": "str", "confidence": 0.0, "evidence": "str"}],\n'
    '  "top_condition": "str",\n'
    '  "top_confidence": 0.0,\n'
    '  "required_capabilities": ["str"],\n'
    '  "critical_handoff_facts": ["str"],\n'
    '  "conflict_flags": ["str"],\n'
    '  "reasoning": "str",\n'
    f'  "disclaimer": "{DISCLAIMER}"\n'
    '}'
)

_CAPS_MAP: dict[str, list[str]] = {
    "cardiac_arrest":  ["cath_lab", "icu", "cardiology"],
    "stemi":           ["cath_lab", "cardiology"],
    "cardiac_event":   ["cath_lab", "cardiology", "icu"],
    "stroke":          ["comprehensive_stroke_center", "neurology"],
    "anaphylaxis":     ["er_basic", "icu"],
    "heat_emergency":  ["er_basic", "icu"],
}


def _hf_client():
    try:
        from openai import OpenAI
        key = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN") or ""
        if not key:
            return None
        return OpenAI(base_url=HF_ROUTER_BASE_URL, api_key=key)
    except ImportError:
        return None


async def run_triage_agent(
    patient_id: str,
    symptoms: str,
    signal_bundle: SignalBundle,
) -> dict:
    # Step 1 — Clinical NER
    entities = extract_clinical_entities(symptoms)
    speech_flags = detect_speech_quality(symptoms)

    # Step 2 — FHIR patient history
    patient_data = load_patient_bundle(patient_id)

    # Step 3 — Sensor validation
    verdict, sensor_reason, sensor_count = collide_and_resolve(signal_bundle)
    conflicts = detect_conflicts(signal_bundle)

    # Step 4 — Deterministic detection
    detections = run_all_detections(signal_bundle)
    esi_level  = score_esi(detections, signal_bundle)

    # Step 5 — RAG retrieval
    top_name = detections[0][0] if detections and detections[0][1] else "unknown"
    protocols = retrieve_relevant_protocols(f"{symptoms} {top_name} emergency triage", n_results=3)

    # Step 6 — Build LLM context
    history = {
        "age": signal_bundle.age, "blood_type": signal_bundle.blood_type,
        "conditions": signal_bundle.conditions, "medications": signal_bundle.medications,
        "allergies": signal_bundle.allergies,
    }
    prompt = build_grounded_prompt(symptoms, history, protocols)
    prompt += (
        f"\nSENSOR VERDICT: {verdict.value} | agreement_count={sensor_count} | {sensor_reason}\n"
        f"CONFLICTS: {conflicts}\n"
        f"DETECTIONS: {[(d[0], d[1], round(d[2], 2)) for d in detections[:3]]}\n"
        f"ESI_LEVEL: {esi_level}\n"
        f"NER_SYMPTOMS: {[e['text'] for e in entities.get('symptoms', [])]}\n"
        + _JSON_SCHEMA
    )

    # Step 7 — HuggingFace LLM call (with fallback)
    agent_out = None
    model_used = "deterministic_fallback"
    client = _hf_client()
    if client:
        for model in (HF_PRIMARY_MODEL, *HF_FALLBACK_MODELS):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user",   "content": prompt},
                    ],
                    max_tokens=1000,
                    temperature=0.1,
                )
                raw   = resp.choices[0].message.content
                clean = raw.replace("```json", "").replace("```", "").strip()
                agent_out  = json.loads(clean)
                model_used = model
                break
            except Exception:
                continue

    if agent_out is None:
        agent_out  = _deterministic_assessment(detections, esi_level, entities, conflicts)
        model_used = "deterministic_fallback"

    # Step 8 — Routing (always deterministic)
    top_detected = next((d[0] for d in detections if d[1]), "unknown_severe")
    diagnosis = WorkingDiagnosis(
        differential=[(d[0], d[2]) for d in detections if d[1]],
        top_condition=agent_out.get("top_condition", top_detected),
        top_confidence=float(agent_out.get("top_confidence", detections[0][2] if detections and detections[0][1] else 0.5)),
        required_capabilities=agent_out.get("required_capabilities", ["er_basic", "icu"]),
        esi_level=esi_level,
        critical_handoff_facts=agent_out.get("critical_handoff_facts", []),
        conflict_flags=conflicts,
        reasoning_trace=agent_out.get("reasoning", "Deterministic assessment"),
    )
    routing = route(diagnosis, signal_bundle.gps)

    # Step 9 — FHIR bundle
    fhir_bundle = generate_handoff_bundle(patient_id, diagnosis, signal_bundle)
    handoff_txt = format_handoff_summary(diagnosis, signal_bundle, patient_data)

    # Step 10 — Return
    return {
        "working_diagnosis": {
            "differential":          diagnosis.differential,
            "top_condition":         diagnosis.top_condition,
            "top_confidence":        diagnosis.top_confidence,
            "esi_level":             diagnosis.esi_level,
            "required_capabilities": diagnosis.required_capabilities,
            "critical_handoff_facts":diagnosis.critical_handoff_facts,
            "conflict_flags":        diagnosis.conflict_flags,
            "reasoning_trace":       diagnosis.reasoning_trace,
        },
        "routing_decision": {
            "chosen_hospital":        routing.chosen_hospital,
            "eta_minutes":            routing.eta_minutes,
            "reasoning":              routing.reasoning,
            "alternatives":           routing.alternatives,
            "fallback_triggered":     routing.fallback_triggered,
            "re_evaluation_triggers": routing.re_evaluation_triggers,
        },
        "fhir_bundle":         fhir_bundle,
        "handoff_summary":     handoff_txt,
        "clinical_entities":   entities,
        "rag_protocol_sources":protocols,
        "sensor_validation": {
            "verdict":          verdict.value,
            "reasoning":        sensor_reason,
            "agreement_count":  sensor_count,
        },
        "agent_reasoning": agent_out.get("reasoning", ""),
        "model_used":      model_used,
        "disclaimer":      DISCLAIMER,
        "also_call_911":   True,
        "technologies_used": {
            "llm":           "aaditya/Llama3-OpenBioLLM-70B via HuggingFace Inference API",
            "llm_fallback":  "Qwen/Qwen2.5-Coder-32B-Instruct",
            "ner":           "scispaCy en_core_sci_md (keyword fallback if unavailable)",
            "rag":           "ChromaDB + sentence-transformers/all-MiniLM-L6-v2",
            "fhir":          "FHIR R4 with Synthea synthetic data",
            "terminologies": ["SNOMED CT", "LOINC", "RxNorm"],
            "detection":     "Deterministic rule-based (no LLM)",
            "routing":       "Deterministic capability matching (no LLM)",
            "esi_scoring":   "Deterministic ESI algorithm (no LLM)",
        },
    }


def _deterministic_assessment(
    detections: list, esi_level: int, entities: dict, conflicts: list[str]
) -> dict:
    detected = [(name, conf) for name, flag, conf, _ in detections if flag]
    if not detected:
        top, top_conf, caps = "undifferentiated_emergency", 0.5, ["er_basic", "icu"]
        facts = ["No specific condition detected — monitor all vitals"]
    else:
        top, top_conf = detected[0]
        caps  = _CAPS_MAP.get(top, ["er_basic", "icu"])
        facts = [f"Suspected {top} ({top_conf:.0%} confidence)", f"ESI Level {esi_level}"]

    syms = [e["text"] for e in entities.get("symptoms", [])]
    if syms:
        facts.append(f"Extracted symptoms: {', '.join(syms)}")

    return {
        "suspected_conditions": [{"condition": c, "confidence": conf, "evidence": "deterministic rules"}
                                  for c, conf in detected],
        "top_condition":        top,
        "top_confidence":       top_conf,
        "required_capabilities":caps,
        "critical_handoff_facts":facts,
        "conflict_flags":       conflicts,
        "reasoning":            f"Deterministic-only: ESI {esi_level}, detected {[c for c, _ in detected]}",
        "disclaimer":           DISCLAIMER,
    }
