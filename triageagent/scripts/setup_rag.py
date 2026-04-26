"""
Build the ChromaDB knowledge base from protocol documents.
Run from triageagent/ directory:
    python scripts/setup_rag.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag import initialize_rag, populate_knowledge_base

if __name__ == "__main__":
    print("Initializing RAG system...")
    initialize_rag()
    chunks, docs = populate_knowledge_base()
    print(f"RAG knowledge base built with {chunks} chunks across {docs} documents")
