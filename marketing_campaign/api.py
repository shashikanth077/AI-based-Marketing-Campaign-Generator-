"""FastAPI backend. Run: uvicorn marketing_campaign.api:app --reload"""

import logging
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()

from marketing_campaign import service  # noqa: E402  (after load_dotenv so GROQ_API_KEY is visible)
from marketing_campaign.data import normalize_product_id  # noqa: E402

log = logging.getLogger("marketing_campaign")
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI(title="AI Marketing Campaign Generator", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    service.ensure_db()


class CampaignRequest(BaseModel):
    product_id: str = Field(examples=["P1011"])
    mode: Literal["direct", "agent"] = "direct"
    creative: bool = False
    temperature: float = Field(1.0, ge=0, le=2)
    safety_check: bool = False
    variants: int = Field(1, ge=1, le=3)


@app.get("/api/health")
def health():
    from marketing_campaign.llm import DEFAULT_GUARD_MODEL, DEFAULT_MODEL

    demo = service.is_demo_mode()
    return {"status": "ok", "demo": demo, "model": None if demo else DEFAULT_MODEL,
            "guard_model": None if demo else DEFAULT_GUARD_MODEL}


@app.get("/api/products")
def products():
    return service.list_products()


@app.post("/api/campaigns")
def create_campaign(req: CampaignRequest):
    try:
        normalize_product_id(req.product_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        return service.generate(req.product_id, req.mode, req.creative, req.temperature,
                                req.safety_check, req.variants)
    except service.ProductNotFound:
        raise HTTPException(status_code=404, detail=f"No product found with ID {req.product_id}")
    except Exception as exc:  # LLM / network / rate-limit failures
        log.exception("campaign generation failed")
        hint = ""
        if "model_not_found" in str(exc) or "does not exist" in str(exc):
            hint = (" The Groq model name is not available to your account. Set GROQ_MODEL in .env to a model "
                    "listed at https://console.groq.com/docs/models and restart the server.")
        raise HTTPException(status_code=502, detail=f"Generation failed: {exc}.{hint}")


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = FRONTEND_DIST / full_path
        return FileResponse(candidate if candidate.is_file() else FRONTEND_DIST / "index.html")
