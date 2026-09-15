"""Loads KB docs and synthetic tickets into the database, running each
ticket through the real classify -> route -> retrieve -> draft pipeline so
the dashboard has realistic demo data. Run with: python -m app.seed
"""
import json
from pathlib import Path

from sqlmodel import Session, select

from .db import engine, init_db
from .models import KBDoc, Ticket
from .pipeline import rag
from .pipeline.run import run_pipeline

SEED_DIR = Path(__file__).parent / "seed_data"


def seed_kb(session: Session) -> None:
    existing = session.exec(select(KBDoc)).first()
    if existing:
        print("KB already seeded, skipping.")
        return
    paths = sorted((SEED_DIR / "kb").glob("*.md"))
    for path in paths:
        content = path.read_text(encoding="utf-8")
        title = content.splitlines()[0].lstrip("# ").strip()
        doc = KBDoc(title=title, content=content, tags=path.stem)
        session.add(doc)
    session.commit()
    print(f"Seeded {len(paths)} KB docs.")


def seed_tickets(session: Session) -> None:
    existing = session.exec(select(Ticket)).first()
    if existing:
        print("Tickets already seeded, skipping.")
        return
    tickets_data = json.loads((SEED_DIR / "tickets.json").read_text(encoding="utf-8"))
    for data in tickets_data:
        ticket = Ticket(**data)
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        run_pipeline(ticket, session)
        print(f"Processed ticket #{ticket.id}: {ticket.subject!r} -> {ticket.category}/{ticket.urgency}/{ticket.team}")


def main() -> None:
    init_db()
    with Session(engine) as session:
        seed_kb(session)
        rag.build_index(session)
        seed_tickets(session)


if __name__ == "__main__":
    main()
