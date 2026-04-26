"""
RAG system — ChromaDB + sentence-transformers/all-MiniLM-L6-v2 + LangChain.
Follows hackathon-recommended RAG architecture.
"""
from __future__ import annotations
from pathlib import Path

PROTOCOLS_DIR = Path(__file__).parent / "data" / "protocols"
CHROMA_DIR    = Path(__file__).parent / "data" / "chroma_db"

_collection = None
_embedder   = None


def initialize_rag() -> None:
    global _collection, _embedder
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_or_create_collection("triage_protocols")
        _embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        print(f"RAG init skipped: {e}")
        _collection = None
        _embedder = None


def populate_knowledge_base() -> tuple[int, int]:
    if _collection is None or _embedder is None:
        return 0, 0
    total_chunks = total_docs = 0
    for proto in PROTOCOLS_DIR.glob("*.txt"):
        text = proto.read_text()
        chunks = _chunk(text, 500, 50)
        for i, chunk in enumerate(chunks):
            _collection.upsert(
                ids=[f"{proto.stem}_{i}"],
                documents=[chunk],
                embeddings=[_embedder.encode(chunk).tolist()],
                metadatas=[{"source": proto.name, "chunk": i}],
            )
        total_chunks += len(chunks)
        total_docs += 1
    return total_chunks, total_docs


def retrieve_relevant_protocols(query: str, n_results: int = 3) -> list[str]:
    if _collection is None or _embedder is None:
        return []
    try:
        count = _collection.count()
        if count == 0:
            return []
        results = _collection.query(
            query_embeddings=[_embedder.encode(query).tolist()],
            n_results=min(n_results, count),
        )
        return results["documents"][0] if results["documents"] else []
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        return []


def build_grounded_prompt(symptoms: str, patient_history: dict, retrieved_protocols: list[str]) -> str:
    patient_summary = _fmt_patient(patient_history)
    protocols_text = "\n---\n".join(retrieved_protocols) if retrieved_protocols else "No protocols retrieved."
    return (
        "You are a clinical decision SUPPORT assistant.\n"
        "Answer ONLY based on the patient data and clinical protocols provided below.\n"
        "If the answer is not clearly supported, say 'insufficient data.'\n"
        "Always include confidence levels and cite which protocol supports your assessment.\n\n"
        f"PATIENT DATA:\n{patient_summary}\n\n"
        f"CURRENT SYMPTOMS AND SENSOR DATA:\n{symptoms}\n\n"
        f"RELEVANT CLINICAL PROTOCOLS:\n{protocols_text}\n\n"
        "Provide:\n"
        "1. Suspected condition(s) with confidence and supporting evidence\n"
        "2. ESI level with justification citing the ESI protocol\n"
        "3. Required hospital capabilities citing the capability mapping\n"
        "4. Critical handoff facts for the receiving ER team\n"
        "5. Any conflicts between patient history and current presentation\n\n"
        "Use language like 'possible', 'consistent with', 'suggests'. Never state a definitive diagnosis.\n"
        "End with: 'This is AI-generated preliminary information. Not a clinical diagnosis.'\n"
    )


def _chunk(text: str, size: int, overlap: int) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


def _fmt_patient(h: dict) -> str:
    if not h:
        return "No patient history available."
    lines = []
    if h.get("age"):
        lines.append(f"Age: {h['age']}")
    if h.get("blood_type"):
        lines.append(f"Blood type: {h['blood_type']}")
    if h.get("conditions"):
        lines.append(f"Conditions: {', '.join(h['conditions'])}")
    if h.get("medications"):
        lines.append(f"Medications: {', '.join(h['medications'])}")
    if h.get("allergies"):
        lines.append(f"Allergies: {', '.join(h['allergies'])}")
    return "\n".join(lines) or "Minimal history available."
