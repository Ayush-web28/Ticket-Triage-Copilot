const COLORS: Record<string, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",

  positive: "bg-emerald-100 text-emerald-700",
  neutral: "bg-slate-100 text-slate-600",
  negative: "bg-orange-100 text-orange-700",
  angry: "bg-red-100 text-red-700",

  new: "bg-blue-100 text-blue-700",
  processing: "bg-blue-100 text-blue-700",
  needs_review: "bg-amber-100 text-amber-700",
  approved: "bg-emerald-100 text-emerald-700",
  escalated: "bg-red-100 text-red-700",

  billing: "bg-violet-100 text-violet-700",
  technical: "bg-cyan-100 text-cyan-700",
  account: "bg-indigo-100 text-indigo-700",
  security: "bg-red-100 text-red-700",
  shipping: "bg-teal-100 text-teal-700",
  feature_request: "bg-pink-100 text-pink-700",
  general: "bg-slate-100 text-slate-600",
};

export default function Badge({ value }: { value: string | null | undefined }) {
  if (!value) return <span className="text-slate-400">—</span>;
  const cls = COLORS[value] ?? "bg-slate-100 text-slate-600";
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>
      {value.replace(/_/g, " ")}
    </span>
  );
}
