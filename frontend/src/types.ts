export type View = "research" | "compare" | "portfolio" | "evidence" | "review" | "evaluation";

export interface UserProfile {
  research_goal?: string | null;
  investment_horizon?: string | null;
  liquidity_need?: string | null;
  loss_tolerance?: string | null;
  investment_experience?: string | null;
  product_knowledge?: string | null;
  concentration_preference?: string | null;
  currency_exposure?: string | null;
  information_preference?: string | null;
  current_task?: string | null;
  missing_information?: string[];
  confidence?: number;
}

export interface Instrument {
  instrument_id: string;
  symbol: string;
  name: string;
  instrument_type: string;
  issuer: string;
  currency: string;
  region: string;
  risk_level: number;
  complexity: string;
  min_horizon_months: number;
  liquidity_days: number;
  expense_ratio: number;
  sectors: Record<string, number>;
  regions: Record<string, number>;
  data_status: string;
  as_of: string;
}

export interface Evidence {
  document_id: string;
  title: string;
  document_type: string;
  source_name: string;
  source_url: string;
  published_at: string;
  retrieved_at: string;
  excerpt: string;
  score: number;
  freshness: string;
  data_status: string;
}

export interface Calculation {
  metric: string;
  value: number | Record<string, number> | null;
  unit: string;
  formula: string;
  assumptions: string[];
  data_status: string;
}

export interface Clarification {
  selected: null | {
    field: string;
    question: string;
    information_gain: number;
    outcome_entropy: number;
    answer_entropy: number;
    possible_policy_outcomes: string[];
    reason: string;
  };
  candidates: Array<{
    field: string;
    information_gain: number;
    question: string;
  }>;
  required_fields: string[];
  missing_fields: string[];
}

export interface ResearchResponse {
  session_id: string;
  intent: string;
  outcome: string;
  message: string;
  disclaimer: string;
  task_confidence: number;
  profile: UserProfile;
  clarification?: Clarification | null;
  evidence: Evidence[];
  conflicts: Array<{ instrument_id: string; fact_key: string; values: Record<string, string>; document_ids: string[] }>;
  calculations: Calculation[];
  claims: Array<{ text: string; citation_ids: string[]; synthetic: boolean }>;
  policy: { outcome: string; rationale: string; hits: Array<{ rule_id: string; severity: string; message: string }> };
  audit_id: string;
  limitations: string[];
}
