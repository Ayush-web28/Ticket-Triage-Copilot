import type { Stats } from "../types";

function shortModel(id: string): string {
  const name = id.split("/").pop() ?? id;
  return name;
}

export default function StatsBar({ stats }: { stats: Stats }) {
  const resolved = (stats.by_status["approved"] ?? 0) as number;
  const needsReview = (stats.by_status["needs_review"] ?? 0) as number;
  const escalated = (stats.by_status["escalated"] ?? 0) as number;

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
      <StatCard label="Total tickets" value={stats.total} />
      <StatCard label="Needs review" value={needsReview} accent="text-amber-600" />
      <StatCard label="Escalated" value={escalated} accent="text-red-600" />
      <StatCard label="Approved" value={resolved} accent="text-emerald-600" />
      <StatCard
        label="Nano classify"
        value={`${stats.avg_latency_ms.classify_nano}ms`}
        sub={shortModel(stats.models.nano)}
      />
      <StatCard
        label="Super route"
        value={`${stats.avg_latency_ms.route_super}ms`}
        sub={shortModel(stats.models.super)}
      />
      <StatCard
        label="Ultra draft"
        value={`${stats.avg_latency_ms.draft_ultra}ms`}
        sub={shortModel(stats.models.ultra)}
      />
    </div>
  );
}

function StatCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</div>
      <div className={`mt-1 text-xl font-semibold ${accent ?? "text-slate-900"}`}>{value}</div>
      {sub && <div className="mt-0.5 truncate text-[11px] text-slate-400" title={sub}>{sub}</div>}
    </div>
  );
}
