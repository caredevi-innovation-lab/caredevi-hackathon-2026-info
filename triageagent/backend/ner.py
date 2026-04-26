"""
Clinical NER — scispaCy en_core_sci_md with SNOMED CT keyword fallback.
HuggingFace alternative: johnsnowlabs/JSL-MedS-NER-q16_v2
"""
from __future__ import annotations
import re

SNOMED_MAP: dict[str, tuple[str, str]] = {
    "chest pain":            ("29857009",  "Chest pain"),
    "chest tightness":       ("29857009",  "Chest pain"),
    "headache":              ("25064002",  "Headache"),
    "shortness of breath":   ("267036007", "Dyspnea"),
    "difficulty breathing":  ("230145002", "Difficulty breathing"),
    "dizziness":             ("404640003", "Dizziness"),
    "nausea":                ("422587007", "Nausea"),
    "vomiting":              ("422400008", "Vomiting"),
    "weakness":              ("13791008",  "Asthenia"),
    "numbness":              ("44077006",  "Numbness"),
    "confusion":             ("40917007",  "Confusion"),
    "seizure":               ("91175000",  "Seizure"),
    "bleeding":              ("131148009", "Bleeding"),
    "swelling":              ("65124004",  "Swelling"),
    "palpitations":          ("80313002",  "Palpitations"),
    "fainting":              ("271594007", "Syncope"),
    "sweating":              ("415690000", "Sweating"),
    "diaphoresis":           ("415690000", "Sweating"),
    "unresponsive":          ("40701008",  "Unresponsive"),
    "no pulse":              ("249530007", "Absent pulse"),
    "arm pain":              ("102588006", "Pain radiating to left arm"),
    "jaw pain":              ("57676002",  "Joint pain"),
    "back pain":             ("161891005", "Back pain"),
    "throat swelling":       ("65124004",  "Swelling"),
    "hives":                 ("126485001", "Urticaria"),
    "rash":                  ("271807003", "Rash"),
    "facial drooping":       ("367521006", "Facial paresis"),
    "arm weakness":          ("299377003", "Arm weakness"),
    "slurred speech":        ("289195008", "Dysarthria"),
}

_SEVERITY_WORDS  = {"severe", "intense", "crushing", "sharp", "tight", "mild", "moderate", "worst", "pressure", "burning"}
_TEMPORAL_WORDS  = {"sudden", "gradual", "minutes ago", "hours ago", "started", "began", "since", "suddenly"}
_BODY_PARTS      = {"chest", "arm", "leg", "head", "back", "jaw", "neck", "throat", "abdomen", "face", "shoulder"}
_NEGATION_PATS   = [r"no\s+{e}", r"denies?\s+{e}", r"without\s+{e}", r"not\s+having\s+{e}", r"not\s+experiencing\s+{e}"]

_nlp = None


def load_ner_model() -> None:
    global _nlp
    try:
        import spacy
        _nlp = spacy.load("en_core_sci_md")
    except Exception:
        _nlp = None


def extract_clinical_entities(text: str) -> dict:
    if _nlp is not None:
        return _extract_scispacy(text)
    return _extract_keywords(text)


def _extract_scispacy(text: str) -> dict:
    doc = _nlp(text)
    symptoms = []
    for ent in doc.ents:
        code, display = map_to_snomed(ent.text.lower())
        symptoms.append({"text": ent.text, "category": ent.label_.lower(),
                         "snomed_code": code, "snomed_display": display})
    body_parts = [bp for bp in _BODY_PARTS if bp in text.lower()]
    negated = detect_negation(text, [s["text"] for s in symptoms])
    return {
        "symptoms": symptoms, "body_parts": body_parts,
        "severity_indicators": _extract_severity(text),
        "temporal_indicators": _extract_temporal(text),
        "negated_findings": negated,
        "speech_quality_flags": detect_speech_quality(text),
        "model_used": "scispacy_en_core_sci_md",
    }


def _extract_keywords(text: str) -> dict:
    tl = text.lower()
    symptoms = []
    for kw, (code, display) in SNOMED_MAP.items():
        if kw in tl:
            symptoms.append({"text": kw, "category": kw.replace(" ", "_"),
                             "snomed_code": code, "snomed_display": display})
    body_parts = [bp for bp in _BODY_PARTS if bp in tl]
    negated = detect_negation(text, [s["text"] for s in symptoms])
    return {
        "symptoms": symptoms, "body_parts": body_parts,
        "severity_indicators": _extract_severity(text),
        "temporal_indicators": _extract_temporal(text),
        "negated_findings": negated,
        "speech_quality_flags": detect_speech_quality(text),
        "model_used": "keyword_fallback",
    }


def detect_negation(text: str, entities: list[str]) -> list[str]:
    negated = []
    for entity in entities:
        ep = re.escape(entity)
        for pat in _NEGATION_PATS:
            if re.search(pat.format(e=ep), text, re.IGNORECASE):
                negated.append(entity)
                break
    return negated


def detect_speech_quality(transcript: str) -> list[str]:
    if not transcript:
        return ["no_speech"]
    flags: list[str] = []
    words = transcript.split()
    if len(words) < 5:
        flags.append("minimal_response")
    sentences = [s for s in re.split(r"[.!?]+", transcript.strip()) if s.strip()]
    avg_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    if avg_len < 3:
        flags.append("truncated")
    counts: dict[str, int] = {}
    for w in words:
        counts[w.lower()] = counts.get(w.lower(), 0) + 1
    if any(c > 2 for c in counts.values()):
        flags.append("confused")
    if re.search(r"\bum+\b|\buh+\b|\.\.\.", transcript, re.IGNORECASE):
        flags.append("slurred")
    return flags or ["normal"]


def map_to_snomed(entity_text: str) -> tuple[str, str]:
    for key, (code, display) in SNOMED_MAP.items():
        if key in entity_text or entity_text in key:
            return code, display
    return ("unknown", entity_text)


def _extract_severity(text: str) -> list[str]:
    return [w for w in _SEVERITY_WORDS if w in text.lower()]


def _extract_temporal(text: str) -> list[str]:
    return [w for w in _TEMPORAL_WORDS if w in text.lower()]
