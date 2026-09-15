export type Status = "new" | "processing" | "needs_review" | "approved" | "escalated";

export interface TraceStep {
  stage: string;
  model: string;
  latency_ms: number;
  output: Record<string, unknown>;
}

export interface KBSource {
  id: number;
  title: string;
  content: string;
  score: number;
}

export interface Ticket {
  id: number;
  subject: string;
  body: string;
  customer_email: string;
  created_at: string;
  status: Status;
  category: string | null;
  urgency: string | null;
  sentiment: string | null;
  priority: number | null;
  team: string | null;
  escalate: boolean;
  routing_reason: string | null;
  draft_reply: string | null;
  final_reply: string | null;
  kb_sources: KBSource[];
  trace: TraceStep[];
}

export interface Stats {
  total: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  by_team: Record<string, number>;
  avg_latency_ms: {
    classify_nano: number;
    route_super: number;
    draft_ultra: number;
  };
  models: {
    nano: string;
    super: string;
    ultra: string;
    embedding: string;
  };
  mock_mode: boolean;
}
