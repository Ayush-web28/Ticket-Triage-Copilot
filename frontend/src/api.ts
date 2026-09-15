import type { Stats, Ticket } from "./types";

// In local dev, vite.config.ts proxies "/api" to the backend. In production
// (frontend and backend deployed separately), set VITE_API_BASE to the full
// backend URL, e.g. https://ticket-triage-backend.onrender.com
const BASE = import.meta.env.VITE_API_BASE ?? "/api";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listTickets: () => fetch(`${BASE}/tickets`).then((r) => json<Ticket[]>(r)),
  getTicket: (id: number) => fetch(`${BASE}/tickets/${id}`).then((r) => json<Ticket>(r)),
  createTicket: (subject: string, body: string, customer_email: string) =>
    fetch(`${BASE}/tickets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject, body, customer_email }),
    }).then((r) => json<Ticket>(r)),
  approveTicket: (id: number) =>
    fetch(`${BASE}/tickets/${id}/approve`, { method: "POST" }).then((r) => json<Ticket>(r)),
  updateReply: (id: number, final_reply: string) =>
    fetch(`${BASE}/tickets/${id}/reply`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ final_reply }),
    }).then((r) => json<Ticket>(r)),
  reprocessTicket: (id: number) =>
    fetch(`${BASE}/tickets/${id}/reprocess`, { method: "POST" }).then((r) => json<Ticket>(r)),
  getStats: () => fetch(`${BASE}/stats`).then((r) => json<Stats>(r)),
};
