import json
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Status(str, Enum):
    new = "new"
    processing = "processing"
    needs_review = "needs_review"
    approved = "approved"
    escalated = "escalated"


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    subject: str
    body: str
    customer_email: str = "customer@example.com"
    created_at: datetime = Field(default_factory=utcnow)

    status: Status = Status.new

    category: str | None = None
    urgency: str | None = None
    sentiment: str | None = None

    priority: int | None = None
    team: str | None = None
    escalate: bool = False
    routing_reason: str | None = None

    draft_reply: str | None = None
    final_reply: str | None = None
    kb_sources_json: str = "[]"

    trace_json: str = "[]"

    def kb_sources(self) -> list[dict]:
        return json.loads(self.kb_sources_json)

    def trace(self) -> list[dict]:
        return json.loads(self.trace_json)


class KBDoc(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str
    tags: str = ""
