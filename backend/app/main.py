import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from .config import settings
from .db import engine, init_db
from .pipeline import rag
from .routes import tickets, stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("triage")

app = FastAPI(title="Ticket Triage Copilot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)
app.include_router(stats.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with Session(engine) as session:
        rag.build_index(session)
    if settings.effective_mock_mode:
        logger.warning(
            "MOCK MODE: no NEBIUS_API_KEY set (or MOCK_MODE=true) -- using rule-based "
            "stand-ins instead of calling Nebius Token Factory. Set NEBIUS_API_KEY in "
            ".env to run the real Nemotron pipeline."
        )
    else:
        logger.info(
            "Live mode: nano=%s super=%s ultra=%s embedding=%s",
            settings.model_nano, settings.model_super, settings.model_ultra, settings.model_embedding,
        )


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": settings.effective_mock_mode}
