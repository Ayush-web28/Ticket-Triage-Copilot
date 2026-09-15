import { useState } from "react";
import { api } from "../api";
import type { Ticket } from "../types";

export default function NewTicketForm({ onCreated }: { onCreated: (t: Ticket) => void }) {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [email, setEmail] = useState("customer@example.com");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!subject.trim() || !body.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const ticket = await api.createTicket(subject, body, email);
      onCreated(ticket);
      setSubject("");
      setBody("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit ticket");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold text-slate-700">Submit a new ticket</h2>
      <div className="space-y-2">
        <input
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
          placeholder="Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />
        <textarea
          className="h-28 w-full resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
          placeholder="Describe the issue..."
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />
        <input
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none"
          placeholder="Customer email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
      <button
        type="submit"
        disabled={submitting}
        className="mt-3 w-full rounded-lg bg-indigo-600 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
      >
        {submitting ? "Running pipeline…" : "Submit & run pipeline"}
      </button>
    </form>
  );
}
