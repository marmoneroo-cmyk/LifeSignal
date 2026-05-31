export type Priority = "critical" | "high" | "preventive" | "informational";

export interface Finding {
  title: string;
  detail: string;
  priority: Priority;
  source: string;
  plain_language: string;
}

export interface TrendPoint {
  taken_on: string;
  value: number;
}

export interface MarkerTrend {
  marker: string;
  label: string;
  unit: string;
  points: TrendPoint[];
  direction: "rising" | "falling" | "stable";
  status: "normal" | "borderline" | "abnormal";
  ref_low?: number | null;
  ref_high?: number | null;
}

export interface ScoreComponent {
  domain: string;
  score: number; // -1 means "no data"
  note: string;
}

export interface UserOut {
  id: number;
  name: string;
  sex: string;
  birth_date: string;
  age: number;
  smoker: boolean;
}

export interface Percentile {
  marker: string;
  label: string;
  value: number;
  percentile: number;
  higher_is_risk: boolean;
}

export interface Copilot {
  questions: string[];
  changes_since_last: string[];
  disclaimer: string;
}

export interface HealthReport {
  user: UserOut;
  health_score: number;
  score_components: ScoreComponent[];
  top_priorities: Finding[];
  findings: Finding[];
  trends: MarkerTrend[];
  missing_screenings: Finding[];
  insurance_insights: Finding[];
  notifications: Finding[];
  emergency_alerts: Finding[];
  drug_interactions: Finding[];
  family_insights: Finding[];
  coverage_matches: Finding[];
  projections: Finding[];
  percentiles: Percentile[];
  second_opinions: Finding[];
  insurance_negotiation: Finding[];
  claim_opportunities: Finding[];
  disclaimer: string;
}

export interface Narrative {
  text: string;
  generated_by: "claude" | "rule_based" | "rule_based_fallback";
  model: string | null;
  disclaimer: string;
}

export interface MarkerMeta {
  key: string;
  label: string;
  unit: string;
}

export interface CoverageMeta {
  key: string;
  label: string;
  critical: boolean;
}
