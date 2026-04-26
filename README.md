# LifeLine AI — Agentic Emergency Triage System

> AI Healthcare Innovation Hackathon 2026 · CareDevi × Gazuntite
> Track: **AI Patient Triage** · **Health Data & Interoperability** · **AI-Powered Care Coordination**

---

## Team Members

| Name | GitHub |
|---|---|
| Alok Thakur | [@aalok012](https://github.com/aalok012) |
| Aayush Raj Sah |  |
---

## Problem Statement

In a cardiac or stroke emergency, every minute without intervention increases permanent damage and mortality. First responders and 911 dispatchers must simultaneously assess symptoms, interpret incomplete sensor data, select the right hospital, and prepare a clinical handoff — all under extreme time pressure, often with no patient history available.

Current triage is reactive: the ER only learns what happened when the ambulance arrives. There is no structured clinical handoff, no capability matching to the receiving hospital, and no AI-augmented decision support available before the patient enters the building.

---

## Solution

**LifeLine AI** is an agentic triage pipeline that runs from the moment a 911 call is placed (or a wearable triggers an alert) through to a FHIR R4 clinical handoff bundle delivered to the receiving hospital before the ambulance arrives.

The agent runs a deterministic-first, LLM-for-synthesis pipeline in ten sequential steps:

1. **Clinical NER** — scispaCy extracts symptoms, medications, and findings from voice/text input
2. **FHIR patient history** — loads Synthea-format patient bundle (conditions, allergies, medications)
3. **Sensor validation** — cross-validates wearable signals (ECG, SpO2, heart rate, fall detection) and flags conflicts
4. **Deterministic detection** — rule-based algorithms detect cardiac arrest, STEMI, stroke, anaphylaxis, and heat emergency without any LLM involvement
5. **ESI scoring** — Emergency Severity Index (1–5) assigned deterministically
6. **RAG retrieval** — ChromaDB retrieves relevant clinical protocols to ground the LLM
7. **LLM synthesis** — Llama3-OpenBioLLM-70B produces a structured JSON differential with confidence scores, grounded only in provided context
8. **Capability-aware routing** — deterministic algorithm matches required capabilities (cath lab, stroke center, PICU) to available hospitals, computing haversine ETA
9. **FHIR R4 bundle generation** — SNOMED CT conditions, LOINC vitals, and patient history assembled into a structured handoff bundle
10. **Clinical handoff summary** — plain-English summary for paramedics with all critical facts and conflict flags

The LLM is used only where it adds value: synthesizing a differential from complex multi-modal context. All safety-critical routing, detection, and ESI scoring is deterministic and auditable.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **LLM (primary)** | `aaditya/Llama3-OpenBioLLM-70B` via HuggingFace Inference API |
| **LLM (fallback)** | `Qwen/Qwen2.5-Coder-32B-Instruct` |
| **Clinical NER** | scispaCy `en_core_sci_md` + keyword fallback |
| **RAG** | ChromaDB · `sentence-transformers/all-MiniLM-L6-v2` · LangChain |
| **FHIR** | FHIR R4 · Synthea synthetic patient data |
| **Terminologies** | SNOMED CT · LOINC · RxNorm · ICD-10-CM |
| **Backend** | FastAPI · Python 3.10+ · Pydantic v2 |
| **Detection / ESI** | Deterministic rule-based (no LLM) |
| **Routing** | Deterministic capability matching + haversine ETA (no LLM) |
| **Frontend** | Vanilla HTML/CSS/JS — patient UI + hospital dashboard |

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- HuggingFace API key (free tier works)

### 1. Clone and enter the project

```bash
git clone https://github.com/aalok012/hackathon-2026-Agentic-Ai.git
cd hackathon-2026-Agentic-Ai/triageagent
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install the scispaCy biomedical model

```bash
pip install https://s3-us-west-2.amazonaws.com/ai2-s3-scispacy/releases/v0.5.4/en_core_sci_md-0.5.4.tar.gz
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set your HuggingFace API key:
# HF_API_KEY=hf_your-key-here
```

### 5. Build the RAG knowledge base

```bash
python scripts/setup_rag.py
```

### 6. Start the API server

```bash
uvicorn backend.main:app --reload
# API running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 7. Open the frontend

Open `frontend/patient.html` directly in your browser (no build step needed).

---

## Key API Endpoints

| Endpoint | Description |
|---|---|
| `POST /triage` | Full agentic triage pipeline — returns differential, routing, FHIR bundle |
| `GET /patients` | List available synthetic patients |
| `GET /patients/{id}` | Load a specific patient's FHIR bundle |
| `GET /hospitals` | List hospitals with capability data |
| `GET /docs` | Interactive Swagger UI |

---

## Architecture

```
Voice/Text Input + Wearable Sensor Data
           │
    ┌──────▼───────┐
    │  Clinical NER │  scispaCy — symptoms, meds, findings
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │  FHIR History │  Synthea patient bundle (conditions, allergies, meds)
    └──────┬───────┘
           │
    ┌──────▼──────────────┐
    │  Sensor Validation  │  Cross-validate ECG, SpO2, HR, fall detection
    └──────┬──────────────┘
           │
    ┌──────▼──────────────┐
    │  Deterministic      │  Cardiac arrest / STEMI / Stroke / Anaphylaxis
    │  Detection + ESI    │  Rule-based, auditable, no LLM
    └──────┬──────────────┘
           │
    ┌──────▼───────┐
    │  RAG Retrieval│  ChromaDB — relevant clinical protocols
    └──────┬───────┘
           │
    ┌──────▼──────────────────────────────┐
    │  LLM Synthesis (Llama3-OpenBioLLM) │  Grounded differential, JSON output
    │  Fallback: Qwen2.5-Coder-32B       │  only from provided context
    └──────┬──────────────────────────────┘
           │
    ┌──────▼───────────────┐
    │  Capability Routing  │  Match to hospital — cath lab, stroke center, etc.
    └──────┬───────────────┘
           │
    ┌──────▼───────────────┐
    │  FHIR R4 Bundle      │  SNOMED CT + LOINC + patient history
    └──────┬───────────────┘
           │
    Hospital Handoff (before ambulance arrives)
```

---

## Screenshots

> The patient UI (`frontend/patient.html`) provides a real-time emergency triage interface. The hospital UI (`frontend/hospital.html`) shows incoming handoff bundles.

---

## Disclaimer

This prototype is for informational and demonstration purposes only. It is not a certified medical device. All AI outputs are preliminary assessments and must be verified by licensed clinical professionals. Do not use for actual patient care decisions.
