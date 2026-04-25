"""
main.py — FastAPI application entry point.
Endpoints wired in later steps; this stub just confirms the server starts.
"""
from fastapi import FastAPI

app = FastAPI(title="TriageAgent", version="0.1.0")


@app.get("/")
async def root():
    return {"status": "ok", "message": "TriageAgent API is running"}
