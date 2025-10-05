import { InsightSummarizeRequest, InsightSummary } from "./types";

export const insightSampleRequest: InsightSummarizeRequest = {
  scope: "national",
  period: "2024-09",
  kpi: {
    name: "Выручка",
    unit: "₸",
    plan: 5_200_000_000,
    actual: 4_800_000_000,
    wow_percent: -7.2,
    mom_percent: -3.5,
  },
  pops: [
    { name: "Сеть A", delta_percent: -12 },
    { name: "Регион Юг", delta_percent: -8.1 },
  ],
  anomalies: [
    {
      dimension: "Сеть A",
      metric: "Выручка",
      severity: "high",
      description: "Падение продаж Reno 11 на 25%",
    },
  ],
  tops: {
    drops: [
      { name: "Сеть A", delta_percent: -12 },
      { name: "Сеть B", delta_percent: -5 },
    ],
    gains: [{ name: "Сеть C", delta_percent: 4.5 }],
  },
};

export const insightSampleResponse: InsightSummary = {
  headline: "Выручка просела на 7.7% от плана в период 2024-09.",
  bullets: [
    "Факт 4.8 млрд ₸ против плана 5.2 млрд ₸ (-7.7%).",
    "Динамика: WoW −7.2%, MoM −3.5%.",
    "Главное падение: Сеть A (−12.0%), прирост: Сеть C (+4.5%).",
    "Аномалия: Сеть A — Падение продаж Reno 11 на 25%.",
  ],
  actions: [
    { label: "Создать задачу супервизору", action: "create_supervisor_task" },
    { label: "Открыть бонус-сетку", action: "open_bonus_grid" },
    { label: "Отфильтровать по SKU/сети", action: "open_filters" },
  ],
};
