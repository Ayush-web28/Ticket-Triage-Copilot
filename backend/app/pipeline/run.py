import json

from sqlmodel import Session

from ..config import settings
from ..models import Ticket, Status
from . import classify, route, rag, draft


def run_pipeline(ticket: Ticket, session: Session) -> Ticket:
    trace = []

    classification, t_nano = classify.classify(ticket.subject, ticket.body)
    trace.append({"stage": "classify", "model": settings.model_nano, "latency_ms": t_nano, "output": classification})
    ticket.category = classification["category"]
    ticket.urgency = classification["urgency"]
    ticket.sentiment = classification["sentiment"]

    routing, t_super = route.route(classification, ticket.subject, ticket.body)
    trace.append({"stage": "route", "model": settings.model_super, "latency_ms": t_super, "output": routing})
    ticket.priority = routing["priority"]
    ticket.team = routing["team"]
    ticket.escalate = routing["escalate"]
    ticket.routing_reason = routing.get("reason", "")

    kb_snippets = rag.retrieve(f"{ticket.subject} {ticket.body}", k=3)
    trace.append({"stage": "retrieve", "model": settings.model_embedding, "latency_ms": 0, "output": {"hits": [s["title"] for s in kb_snippets]}})

    drafted, t_ultra = draft.draft(ticket.subject, ticket.body, classification, routing, kb_snippets)
    trace.append({"stage": "draft", "model": settings.model_ultra, "latency_ms": t_ultra, "output": {"confidence": drafted.get("confidence")}})
    ticket.draft_reply = drafted["reply"]
    ticket.kb_sources_json = json.dumps(kb_snippets)

    ticket.status = Status.escalated if ticket.escalate else Status.needs_review
    ticket.trace_json = json.dumps(trace)

    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket
