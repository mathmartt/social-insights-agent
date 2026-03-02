"""
Social Insights Agent — FastAPI backend
Run: GEMINI_API_KEY=your_key uvicorn main:app --reload --port 8000
"""
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from services.data_service import DataService
from services.gemini_service import GeminiService
from services.export_service import ExportService

# ─── App & middleware ─────────────────────────────────────────────────────────

app = FastAPI(title="Social Insights Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup ──────────────────────────────────────────────────────────────────

DATA_PATH = Path(__file__).parent / "data" / "mock_data.csv"
data_service = DataService(str(DATA_PATH))

GEMINI_API_KEY: str = ""


@app.on_event("startup")
def startup():
    global GEMINI_API_KEY
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    if not GEMINI_API_KEY:
        print("⚠️   GEMINI_API_KEY environment variable not set.")
    else:
        print("✅  Gemini API key loaded.")

    if DATA_PATH.exists():
        data_service.load_data()
        print(f"✅  Loaded {data_service.get_info()['total_rows']} rows from {DATA_PATH}")
    else:
        print(f"⚠️   CSV not found at {DATA_PATH}. Run generate_mock_data.py first.")


def _get_gemini_service() -> GeminiService:
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured on the server. "
                   "Set the environment variable and restart.",
        )
    return GeminiService(GEMINI_API_KEY)


# ─── Request models ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str


class FollowUpRequest(BaseModel):
    query: str
    conversation_history: list = []
    current_results: dict = {}


class ExportRequest(BaseModel):
    data: dict


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "data_loaded": data_service.df is not None,
        "api_key_set": bool(GEMINI_API_KEY),
    }


@app.get("/api/data-info")
def data_info():
    return data_service.get_info()


@app.post("/api/query")
def process_query(req: QueryRequest):
    svc = _get_gemini_service()

    info = data_service.get_info()
    if not info.get("loaded"):
        raise HTTPException(
            status_code=503,
            detail="Data not loaded. Place a CSV at backend/data/mock_data.csv and restart.",
        )

    candidates = data_service.filter_candidates(req.query)
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidate comments found.")

    try:
        result = svc.analyze(req.query, candidates, info)
    except Exception as exc:
        _raise_ai_error(exc)

    return result


@app.post("/api/follow-up")
def process_follow_up(req: FollowUpRequest):
    svc = _get_gemini_service()

    info = data_service.get_info()
    if not info.get("loaded"):
        raise HTTPException(status_code=503, detail="Data not loaded.")

    candidates = data_service.filter_candidates(req.query)

    try:
        result = svc.follow_up(
            req.query,
            candidates,
            req.conversation_history,
            req.current_results,
        )
    except Exception as exc:
        _raise_ai_error(exc)

    return result


@app.post("/api/export/pptx")
def export_pptx(req: ExportRequest):
    try:
        svc = ExportService()
        pptx_bytes = svc.create_pptx_bytes(req.data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Export failed: {exc}")

    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=social_insights_report.pptx"},
    )


@app.post("/api/export/csv")
def export_csv(req: ExportRequest):
    comments = req.data.get("relevant_comments", [])
    try:
        svc = ExportService()
        csv_bytes = svc.create_csv_bytes(comments)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Export failed: {exc}")

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=relevant_comments.csv"},
    )


# ─── Error helper ─────────────────────────────────────────────────────────────

def _raise_ai_error(exc: Exception):
    msg = str(exc)
    if "authentication" in msg.lower() or "api_key" in msg.lower() or "401" in msg:
        raise HTTPException(status_code=401, detail="Invalid Gemini API key.")
    if "rate" in msg.lower() or "429" in msg:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait a moment.")
    raise HTTPException(status_code=500, detail=f"AI processing error: {msg}")
