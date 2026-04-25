# TriageAgent 🚑

An AI-powered emergency triage system that detects cardiac events from wearable signals, determines the working diagnosis, and routes patients to the best-fit hospital — all in real time.

---

## Architecture

```
triageagent/
├── backend/
│   ├── main.py          FastAPI app entry (endpoints: /detect, /triage, /hospitals)
│   ├── models.py        Core dataclasses: SignalBundle, WorkingDiagnosis, RoutingDecision
│   ├── signals.py       Signal weighting + conflict detection
│   ├── detection.py     Cardiac arrest detection (pure rules, no LLM)
│   ├── routing.py       Hospital capability matching logic
│   ├── agent.py         Claude Haiku agent + tool definitions
│   ├── fhir.py          FHIR R4 Bundle generation
│   └── data/
│       ├── hospitals.json       Mock hospital registry
│       └── patients/            Synthea-style FHIR patient bundles
├── frontend/
│   └── demo.html        Watch + phone single-page demo UI
├── .env                 API keys — never commit
└── requirements.txt
```

---

## Quickstart

### 1. Clone & create virtual environment

```bash
cd triageagent
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env` and add your Anthropic API key:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-haiku-4-5
```

### 4. Run the API server

```bash
uvicorn backend.main:app --reload --port 8000
```

Server starts at **http://localhost:8000**

---

## API Endpoints

| Method | Path         | Description                                              |
|--------|-------------|----------------------------------------------------------|
| GET    | `/`          | Health check                                             |
| GET    | `/hospitals` | List all hospitals with capabilities and ER wait times   |
| POST   | `/detect`    | Accept wearable signals → return cardiac arrest detection|
| POST   | `/triage`    | Full agent + routing flow → RoutingDecision + FHIR Bundle|

### Example: Detect cardiac arrest

```bash
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "heart_rate": 0,
    "spo2": 72,
    "accelerometer": {"x": 0, "y": 0, "z": 0},
    "patient_id": "patient-001"
  }'
```

### Example: Full triage

```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "chest pain radiating to left arm, diaphoresis",
    "patient_id": "patient-001"
  }'
```

---

## Key Concepts

### SignalBundle
Raw sensor data from the wearable: heart rate, SpO₂, accelerometer, GPS, patient-reported symptoms.

### WorkingDiagnosis
The agent's best guess: condition label, confidence score, urgency level, and supporting evidence.

### RoutingDecision
The final output: chosen hospital, ETA, capability match score, and a plain-English reasoning string for the paramedic handoff.

---

## Detection Logic (no LLM)

Cardiac arrest is flagged when **three or more** of the following are true:
- Heart rate = 0 or undetectable
- SpO₂ < 80 %
- No movement for > 30 s after a fall event
- Patient unresponsive (no button press acknowledgment)

Athletes with low resting HR and isolated fall events are explicitly excluded.

---

## Hospital Routing

Conditions are mapped to required capabilities:

| Diagnosis          | Required Capability          |
|--------------------|------------------------------|
| STEMI              | `cath_lab`                   |
| Ischemic stroke    | `comprehensive_stroke_center`|
| Major trauma       | `level_1_trauma`             |
| Pediatric emergency| `pediatric_er`               |
| Uncertain / severe | Broadest-capability fallback |

The routing algorithm scores each hospital on capability match, distance, and current ER wait time.

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| API        | FastAPI + Uvicorn                 |
| AI Agent   | Anthropic Claude Haiku 4.5        |
| FHIR       | fhir.resources (R4)               |
| Validation | Pydantic v2                       |
| Frontend   | Vanilla HTML/CSS/JS (no framework)|

---

## Development Steps

1. ✅ Project skeleton & dependencies
2. ⬜ Data structures (`models.py`)
3. ⬜ Mock data (hospitals + patients)
4. ⬜ Detection layer (`detection.py`)
5. ⬜ Signal weighting (`signals.py`)
6. ⬜ Routing layer (`routing.py`)
7. ⬜ Claude agent layer (`agent.py`)
8. ⬜ FHIR Bundle generator (`fhir.py`)
9. ⬜ Wire everything in `main.py`
10. ⬜ Demo UI (`demo.html`)

---

## License

MIT — built for the CareDevi Hackathon 2026.
