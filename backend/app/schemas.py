from datetime import datetime

from pydantic import BaseModel

from .models import Status


class TicketCreate(BaseModel):
    subject: str
    body: str
    customer_email: str = "customer@example.com"


class TicketOut(BaseModel):
    id: int
    subject: str
    body: str
    customer_email: str
    created_at: datetime
    status: Status
    category: str | None
    urgency: str | None
    sentiment: str | None
    priority: int | None
    team: str | None
    escalate: bool
    routing_reason: str | None
    draft_reply: str | None
    final_reply: str | None
    kb_sources: list[dict]
    trace: list[dict]

    @classmethod
    def from_ticket(cls, t) -> "TicketOut":
        return cls(
            id=t.id,
            subject=t.subject,
            body=t.body,
            customer_email=t.customer_email,
            created_at=t.created_at,
            status=t.status,
            category=t.category,
            urgency=t.urgency,
            sentiment=t.sentiment,
            priority=t.priority,
            team=t.team,
            escalate=t.escalate,
            routing_reason=t.routing_reason,
            draft_reply=t.draft_reply,
            final_reply=t.final_reply,
            kb_sources=t.kb_sources(),
            trace=t.trace(),
        )


class ReplyUpdate(BaseModel):
    final_reply: str
