import { useEffect, useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { isAxiosError } from "axios";

import { api } from "../../shared/api/http";
import { featureFlags } from "../../shared/config/featureFlags";
import type { InsightSummarizeRequest, InsightSummary } from "../../entities/insight/types";

interface Props {
  request: InsightSummarizeRequest;
}

export function ActionableInsightsWidget({ request }: Props) {
  const [summary, setSummary] = useState<InsightSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(featureFlags.aiInsights);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!featureFlags.aiInsights) {
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    api.insights
      .summarize(request)
      .then((response) => {
        if (cancelled) return;
        setSummary(response.data as InsightSummary);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (isAxiosError(err)) {
          const data = err.response?.data as { detail?: string; code?: string } | undefined;
          if (data?.code === "feature_disabled") {
            setError("Модуль AI-инсайтов отключён (feature flag).");
          } else {
            setError(data?.detail || err.message || "Не удалось получить инсайты");
          }
          return;
        }
        const generic = err instanceof Error ? err.message : null;
        setError(generic || "Не удалось получить инсайты");
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [request]);

  if (!featureFlags.aiInsights) {
    return null;
  }

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-slate-700">
            <Sparkles className="h-5 w-5 text-amber-500" />
            <h2 className="text-xl font-semibold">Что делать?</h2>
          </div>
          {summary?.headline && (
            <p className="mt-2 text-sm text-slate-500">{summary.headline}</p>
          )}
        </div>
        {loading && <Loader2 className="h-5 w-5 animate-spin text-slate-400" />}
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600">
          {error}
        </div>
      )}

      {!error && summary && summary.bullets.length > 0 && (
        <ul className="mt-4 space-y-2 text-sm text-slate-600">
          {summary.bullets.map((bullet, index) => (
            <li key={index} className="flex gap-2">
              <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-amber-500" />
              <span>{bullet}</span>
            </li>
          ))}
        </ul>
      )}

      {!error && summary && summary.actions.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-2">
          {summary.actions.map((action) => (
            <button
              key={action.action}
              type="button"
              onClick={() => console.info("insight-action", action.action)}
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-slate-900 hover:bg-slate-900 hover:text-white"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
