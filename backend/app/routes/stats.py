from collections import Counter

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..config import settings
from ..db import get_session
from ..models import Ticket

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def get_stats(session: Session = Depends(get_session)):
    tickets = session.exec(select(Ticket)).all()

    by_status = Counter(t.status for t in tickets)
    by_category = Counter(t.category for t in tickets if t.category)
    by_team = Counter(t.team for t in tickets if t.team)

    latencies = {"classify": [], "route": [], "draft": []}
    for t in tickets:
        for step in t.trace():
            stage = step.get("stage")
            if stage in ("classify",):
                latencies["classify"].append(step["latency_ms"])
            elif stage == "route":
                latencies["route"].append(step["latency_ms"])
            elif stage == "draft":
                latencies["draft"].append(step["latency_ms"])

    def avg(values: list[int]) -> float:
        return round(sum(values) / len(values), 1) if values else 0.0

    return {
        "total": len(tickets),
        "by_status": {k.value: v for k, v in by_status.items()},
        "by_category": dict(by_category),
        "by_team": dict(by_team),
        "avg_latency_ms": {
            "classify_nano": avg(latencies["classify"]),
            "route_super": avg(latencies["route"]),
            "draft_ultra": avg(latencies["draft"]),
        },
        "models": {
            "nano": settings.model_nano,
            "super": settings.model_super,
            "ultra": settings.model_ultra,
            "embedding": settings.model_embedding,
        },
        "mock_mode": settings.effective_mock_mode,
    }
