import { useEffect, useState } from "react";
import { api } from "./api";
import type { Stats, Ticket } from "./types";
import StatsBar from "./components/StatsBar";
import TicketTable from "./components/TicketTable";
import TicketDetail from "./components/TicketDetail";
import NewTicketForm from "./components/NewTicketForm";

export default function App() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [t, s] = await Promise.all([api.listTickets(), api.getStats()]);
      setTickets(t);
      setStats(s);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reach the API");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  const selected = tickets.find((t) => t.id === selectedId) ?? null;

  function handleCreated(t: Ticket) {
    setTickets((prev) => [t, ...prev]);
    setSelectedId(t.id);
    api.getStats().then(setStats).catch(() => {});
  }

  function handleUpdated(t: Ticket) {
    setTickets((prev) => prev.map((x) => (x.id === t.id ? t : x)));
    api.getStats().then(setStats).catch(() => {});
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-lg font-semibold text-slate-900">Ticket Triage Copilot</h1>
            <p className="text-xs text-slate-400">
              Nemotron Nano classifies → Super routes → Ultra drafts, grounded on your KB — via Nebius Token Factory
            </p>
          </div>
          {stats?.mock_mode && (
            <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
              Mock mode — set NEBIUS_API_KEY for live Nemotron calls
            </span>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-6">
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            Couldn't reach the API: {error}. Is the backend running on port 8000?
          </div>
        )}

        {stats && <StatsBar stats={stats} />}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-700">Queue</h2>
              <button
                onClick={refresh}
                className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
              >
                Refresh
              </button>
            </div>
            {loading ? (
              <p className="text-sm text-slate-400">Loading…</p>
            ) : (
              <TicketTable tickets={tickets} selectedId={selectedId} onSelect={setSelectedId} />
            )}

            {selected && (
              <div className="pt-2">
                <TicketDetail ticket={selected} onUpdated={handleUpdated} />
              </div>
            )}
          </div>

          <div>
            <NewTicketForm onCreated={handleCreated} />
          </div>
        </div>
      </main>
    </div>
  );
}
