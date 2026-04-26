# TriageAgent

**Agentic AI emergency response system with FHIR-native clinical handoff**

## Tech Stack

- **LLM**: HuggingFace — Llama3-OpenBioLLM-70B (primary), Qwen2.5-Coder-32B-Instruct (fallback)
- **Clinical NER**: scispaCy `en_core_sci_md` + SNOMED CT mapping
- **RAG**: ChromaDB + sentence-transformers/all-MiniLM-L6-v2 + LangChain
- **FHIR**: FHIR R4 with Synthea synthetic patient data
- **Terminologies**: SNOMED CT, LOINC, RxNorm, ICD-10-CM
- **Backend**: FastAPI (Python 3.10+)
- **Detection / Routing / ESI**: Deterministic rule-based (no LLM)

## Hackathon

**AI Healthcare Innovation Hackathon 2026**

Tracks: AI Patient Triage · Health Data & Interoperability · AI-Powered Care Coordination

## Run

```bash
pip install -r requirements.txt
python scripts/setup_rag.py          # build ChromaDB knowledge base
uvicorn backend.main:app --reload    # start API on localhost:8000
# open frontend/patient.html in browser
```

## scispaCy model install

```bash
pip install https://s3-us-west-2.amazonaws.com/ai2-s3-scispacy/releases/v0.5.4/en_core_sci_md-0.5.4.tar.gz
```
