export const featureFlags = {
  aiInsights:
    String(import.meta.env.VITE_FEATURE_AI_INSIGHTS ?? "false").toLowerCase() === "true",
} as const;

export type FeatureFlags = typeof featureFlags;

export function isFeatureEnabled<K extends keyof FeatureFlags>(flag: K): FeatureFlags[K] {
  return featureFlags[flag];
}
