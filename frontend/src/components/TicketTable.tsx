import type { Ticket } from "../types";
import Badge from "./Badge";

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso + "Z").getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function TicketTable({
  tickets,
  selectedId,
  onSelect,
}: {
  tickets: Ticket[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}) {
  if (tickets.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-400">
        No tickets yet. Submit one on the right to see the pipeline run.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
          <tr>
            <th className="px-4 py-2 font-medium">Subject</th>
            <th className="px-4 py-2 font-medium">Category</th>
            <th className="px-4 py-2 font-medium">Urgency</th>
            <th className="px-4 py-2 font-medium">Priority</th>
            <th className="px-4 py-2 font-medium">Team</th>
            <th className="px-4 py-2 font-medium">Status</th>
            <th className="px-4 py-2 font-medium">When</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {tickets.map((t) => (
            <tr
              key={t.id}
              onClick={() => onSelect(t.id)}
              className={`cursor-pointer transition-colors hover:bg-slate-50 ${
                selectedId === t.id ? "bg-indigo-50" : ""
              }`}
            >
              <td className="max-w-xs truncate px-4 py-2.5 font-medium text-slate-800">
                {t.escalate && <span className="mr-1.5 text-red-500">⚑</span>}
                {t.subject}
              </td>
              <td className="px-4 py-2.5">
                <Badge value={t.category} />
              </td>
              <td className="px-4 py-2.5">
                <Badge value={t.urgency} />
              </td>
              <td className="px-4 py-2.5 text-slate-600">{t.priority ?? "—"}</td>
              <td className="px-4 py-2.5 text-slate-600">{t.team ?? "—"}</td>
              <td className="px-4 py-2.5">
                <Badge value={t.status} />
              </td>
              <td className="px-4 py-2.5 whitespace-nowrap text-slate-400">{timeAgo(t.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
