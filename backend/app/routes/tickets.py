from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..models import Ticket, Status
from ..pipeline.run import run_pipeline
from ..schemas import TicketCreate, TicketOut, ReplyUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut)
def create_ticket(payload: TicketCreate, session: Session = Depends(get_session)):
    ticket = Ticket(subject=payload.subject, body=payload.body, customer_email=payload.customer_email)
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    ticket = run_pipeline(ticket, session)
    return TicketOut.from_ticket(ticket)


@router.get("", response_model=list[TicketOut])
def list_tickets(session: Session = Depends(get_session)):
    tickets = session.exec(select(Ticket).order_by(Ticket.created_at.desc())).all()
    return [TicketOut.from_ticket(t) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketOut.from_ticket(ticket)


@router.post("/{ticket_id}/approve", response_model=TicketOut)
def approve_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.final_reply = ticket.final_reply or ticket.draft_reply
    ticket.status = Status.approved
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return TicketOut.from_ticket(ticket)


@router.put("/{ticket_id}/reply", response_model=TicketOut)
def update_reply(ticket_id: int, payload: ReplyUpdate, session: Session = Depends(get_session)):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.final_reply = payload.final_reply
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return TicketOut.from_ticket(ticket)


@router.post("/{ticket_id}/reprocess", response_model=TicketOut)
def reprocess_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket = run_pipeline(ticket, session)
    return TicketOut.from_ticket(ticket)
