import axios, { AxiosError, AxiosRequestConfig } from "axios";

import { addOutboxRecord } from "../lib/indexedDb";
import { createId } from "../lib/createId";
import { mockApi } from "./mock";

const BASE_URL = import.meta.env.VITE_API_URL ?? "";
const API_ENABLED = Boolean(BASE_URL);

export const http = axios.create({
  baseURL: BASE_URL,
  timeout: 15_000,
});

http.interceptors.request.use((config) => {
  const headers = config.headers ?? {};
  if (!headers["Idempotency-Key"]) {
    headers["Idempotency-Key"] = createId();
  }
  const stored = localStorage.getItem("oppo-kz::token");
  if (stored) {
    headers.Authorization = `Bearer ${stored}`;
  }
  config.headers = headers;
  return config;
});

http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as AxiosRequestConfig & { retried?: boolean };
    const networkError = !error.response;

    if (networkError && config && !config.retried) {
      const id = createId();
      await addOutboxRecord({
        id,
        endpoint: `${config.method?.toUpperCase() || "GET"} ${config.url}`,
        payload: {
          data: config.data,
          params: config.params,
          headers: config.headers,
          method: config.method,
          url: config.url,
        },
        createdAt: Date.now(),
        status: "pending",
        retries: 0,
      });
      return Promise.reject(new Error("REQUEST_QUEUED"));
    }

    return Promise.reject(error);
  },
);

export const api = {
  health: () => (API_ENABLED ? http.get("/api/v1/health") : Promise.resolve({ data: { status: "mock" } })),
  version: () => (API_ENABLED ? http.get("/api/v1/version") : Promise.resolve({ data: { version: "0.0.0-demo" } })),
  invites: {
    list: () => (API_ENABLED ? http.get("/api/v1/invites") : mockApi.invites.list()),
    create: (body: unknown) => http.post("/api/v1/invites", body),
    revoke: (id: string) => http.delete(`/api/v1/invites/${id}`),
  },
  sales: {
    list: (params?: unknown) => (API_ENABLED ? http.get("/api/v1/sales", { params }) : mockApi.sales.list()),
    create: (body: unknown) => http.post("/api/v1/sales", body),
    update: (id: string, body: unknown) => http.patch(`/api/v1/sales/${id}`, body),
    remove: (id: string) => http.delete(`/api/v1/sales/${id}`),
    corrections: {
      create: (id: string, body: unknown) => http.post(`/api/v1/sales/${id}/corrections`, body),
    },
  },
  plans: {
    list: (params?: unknown) => (API_ENABLED ? http.get("/api/v1/plans", { params }) : mockApi.plans.list()),
    bulk: (body: unknown) => http.post("/api/v1/plans/bulk", body),
  },
  dict: {
    networks: () => (API_ENABLED ? http.get("/api/v1/dict/networks") : mockApi.dict.networks()),
    stores: () => (API_ENABLED ? http.get("/api/v1/dict/stores") : mockApi.dict.stores()),
    regions: () => (API_ENABLED ? http.get("/api/v1/dict/regions") : mockApi.dict.regions()),
  },
  bonus: {
    schemes: () => (API_ENABLED ? http.get("/api/v1/bonus/schemes") : mockApi.bonus.schemes()),
    payouts: (params?: unknown) => (API_ENABLED ? http.get("/api/v1/bonus/payouts", { params }) : mockApi.bonus.payouts()),
  },
  analytics: {
    kpi: (params?: unknown) => (API_ENABLED ? http.get("/api/v1/analytics/kpi", { params }) : Promise.resolve({ data: [] })),
    planVsFact: (params?: unknown) =>
      API_ENABLED ? http.get("/api/v1/analytics/plan-vs-fact", { params }) : Promise.resolve({ data: [] }),
    leaderboard: (params?: unknown) =>
      API_ENABLED ? http.get("/api/v1/analytics/leaderboard", { params }) : Promise.resolve({ data: [] }),
  },
  periods: {
    list: () => (API_ENABLED ? http.get("/api/v1/periods") : Promise.resolve({ data: ["2024-07", "2024-08", "2024-09"] })),
    close: (id: string, body: unknown) => http.post(`/api/v1/periods/${id}/close`, body),
  },
  sync: {
    push: () => (API_ENABLED ? http.post("/api/v1/sync/push", {}) : Promise.resolve({ data: { status: "mock" } })),
    pull: () => (API_ENABLED ? http.post("/api/v1/sync/pull", {}) : Promise.resolve({ data: { status: "mock" } })),
  },
};
