import axios from "axios";

const BASE = import.meta.env.VITE_API_BASE || "";

function authHeader() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: token } : {};
}

export const http = axios.create({
  baseURL: BASE,
});

http.interceptors.request.use((cfg) => {
  cfg.headers = { ...(cfg.headers || {}), ...authHeader() };
  return cfg;
});

export const api = {
  health: () => http.get("/api/v1/health"),
  version: () => http.get("/api/v1/version"),

  auth: {
    login: (body: { username: string; password: string }) => http.post("/api/v1/auth/login", body),
    me: () => http.get("/api/v1/auth/me"),
  },

  stores: {
    list: () => http.get("/api/v1/stores"),
    create: (body: { name: string; city?: string; network?: string }) => http.post("/api/v1/stores", body),
    remove: (id: number) => http.delete(`/api/v1/stores/${id}`),
  },

  sku: {
    list: () => http.get("/api/v1/sku"),
    create: (body: { brand: string; model: string; code: string }) => http.post("/api/v1/sku", body),
    remove: (id: number) => http.delete(`/api/v1/sku/${id}`),
  },

  price: {
    list: (params?: { sku_id?: number; on?: string }) => http.get("/api/v1/price", { params }),
    upsert: (body: { sku_id: number; price: number; valid_from: string; valid_to?: string | null }) =>
      http.post("/api/v1/price", body),
  },

  sales: {
    addPromoterOne: (body: { store_id: number; sku_id: number; sold_at: string; qty: number; amount?: number }) =>
      http.post("/api/v1/sales/promoter/one", body),
  },

  invites: {
    list: (params?: { only_active?: boolean }) => http.get("/api/v1/invites", { params }),
    create: (body: {
      role: "promoter" | "super";
      username: string;
      full_name?: string;
      store_id?: number;
      network?: string;
      expires_hours?: number;
    }) => http.post("/api/v1/invites", body),
    register: (body: { code: string; username: string; full_name?: string; password: string }) =>
      http.post("/api/v1/auth/register-by-invite", body),
    revoke: (id: number) => http.delete(`/api/v1/invites/${id}`),
  },

  bonus: {
    list: (params?: { network?: string; sku_id?: number; active_on?: string }) =>
      http.get("/api/v1/bonus/", { params }),
    create: (body: {
      sku_id?: number | null;
      network?: string | null;
      qty_from?: number | null;
      bonus_per_unit: number;
      valid_from: string;
      valid_to?: string | null;
    }) => http.post("/api/v1/bonus/", body),
    update: (id: number, body: {
      sku_id?: number | null;
      network?: string | null;
      qty_from?: number | null;
      bonus_per_unit: number;
      valid_from: string;
      valid_to?: string | null;
    }) => http.put(`/api/v1/bonus/${id}`, body),
    remove: (id: number) => http.delete(`/api/v1/bonus/${id}`),
  },
,
  audit: {
    list: () => http.get("/api/v1/audit"),
  },


  anomalies: {
    list: (params?: any) => http.get("/api/v1/anomalies", { params }),
  },


  forecast: {
    sku: (code: string, store?: string, period=30) => http.get(`/api/v1/forecast/sku/${code}`, { params: { store, period } }),
  },

};
