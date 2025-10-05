export interface InsightKPI {
  name: string;
  unit?: string | null;
  plan?: number | null;
  actual: number;
  delta?: number | null;
  delta_percent?: number | null;
  wow_percent?: number | null;
  mom_percent?: number | null;
  yoy_percent?: number | null;
}

export interface InsightPopulation {
  name: string;
  value?: number | null;
  delta_percent?: number | null;
}

export interface InsightAnomaly {
  dimension: string;
  metric: string;
  severity?: "low" | "medium" | "high" | null;
  description: string;
}

export interface InsightTopItem {
  name: string;
  value?: number | null;
  delta_percent?: number | null;
}

export interface InsightTopSummary {
  drops?: InsightTopItem[];
  gains?: InsightTopItem[];
}

export interface InsightSummarizeRequest {
  scope: string;
  period: string;
  kpi: InsightKPI;
  pops?: InsightPopulation[];
  anomalies?: InsightAnomaly[];
  tops?: InsightTopSummary;
}

export interface InsightAction {
  label: string;
  action: string;
}

export interface InsightSummary {
  headline: string;
  bullets: string[];
  actions: InsightAction[];
}
