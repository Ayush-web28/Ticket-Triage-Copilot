import { useEffect, useState } from "react";
import { api } from "../api";
import type { Ticket } from "../types";
import Badge from "./Badge";

const STAGE_LABELS: Record<string, string> = {
  classify: "1 · Classify (Nano)",
  route: "2 · Route (Super)",
  retrieve: "3 · Retrieve (RAG)",
  draft: "4 · Draft (Ultra)",
};

export default function TicketDetail({
  ticket,
  onUpdated,
}: {
  ticket: Ticket;
  onUpdated: (t: Ticket) => void;
}) {
  const [reply, setReply] = useState(ticket.final_reply ?? ticket.draft_reply ?? "");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setReply(ticket.final_reply ?? ticket.draft_reply ?? "");
  }, [ticket.id, ticket.draft_reply, ticket.final_reply]);

  async function handleApprove() {
    setSaving(true);
    try {
      if (reply !== ticket.draft_reply) {
        await api.updateReply(ticket.id, reply);
      }
      const updated = await api.approveTicket(ticket.id);
      onUpdated(updated);
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveDraft() {
    setSaving(true);
    try {
      const updated = await api.updateReply(ticket.id, reply);
      onUpdated(updated);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-slate-800">{ticket.subject}</h2>
            <p className="mt-0.5 text-xs text-slate-400">
              {ticket.customer_email} · #{ticket.id}
            </p>
          </div>
          <Badge value={ticket.status} />
        </div>
        <p className="mt-3 whitespace-pre-wrap text-sm text-slate-600">{ticket.body}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          <Badge value={ticket.category} />
          <Badge value={ticket.urgency} />
          <Badge value={ticket.sentiment} />
          {ticket.priority !== null && (
            <span className="inline-block rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
              priority {ticket.priority}/5
            </span>
          )}
          {ticket.team && (
            <span className="inline-block rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
              → {ticket.team.replace(/_/g, " ")}
            </span>
          )}
        </div>
        {ticket.routing_reason && (
          <p className="mt-2 text-xs italic text-slate-400">{ticket.routing_reason}</p>
        )}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-2 text-sm font-semibold text-slate-700">Pipeline trace</h3>
        <ol className="space-y-1.5">
          {ticket.trace.map((step, i) => (
            <li key={i} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-1.5 text-xs">
              <span className="font-medium text-slate-600">{STAGE_LABELS[step.stage] ?? step.stage}</span>
              <span className="text-slate-400">
                {step.model.split("/").pop()} · {step.latency_ms}ms
              </span>
            </li>
          ))}
        </ol>
      </div>

      {ticket.kb_sources.length > 0 && (
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Grounded on</h3>
          <div className="space-y-2">
            {ticket.kb_sources.map((kb) => (
              <details key={kb.id} className="rounded-lg border border-slate-100 bg-slate-50 p-2 text-xs">
                <summary className="cursor-pointer font-medium text-slate-600">{kb.title}</summary>
                <p className="mt-1 whitespace-pre-wrap text-slate-500">{kb.content}</p>
              </details>
            ))}
          </div>
        </div>
      )}

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="mb-2 text-sm font-semibold text-slate-700">
          {ticket.status === "approved" ? "Sent reply" : "Draft reply"}
        </h3>
        <textarea
          className="h-40 w-full resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
          value={reply}
          onChange={(e) => setReply(e.target.value)}
          disabled={ticket.status === "approved"}
        />
        {ticket.status !== "approved" && (
          <div className="mt-3 flex gap-2">
            <button
              onClick={handleApprove}
              disabled={saving}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-700 disabled:opacity-50"
            >
              Approve &amp; send
            </button>
            <button
              onClick={handleSaveDraft}
              disabled={saving || reply === (ticket.final_reply ?? ticket.draft_reply)}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:opacity-50"
            >
              Save edits
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
