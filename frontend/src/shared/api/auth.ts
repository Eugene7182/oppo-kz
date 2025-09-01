// frontend/src/shared/api/auth.ts
import axios from "axios";

const BASE_URL =
  (import.meta as any).env?.VITE_API_URL?.toString()?.replace(/\/+$/, "") ||
  "/api/v1";

const TOKEN_KEY = "AUTH_TOKEN";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function setToken(t: string | null) {
  if (t) localStorage.setItem(TOKEN_KEY, t);
  else localStorage.removeItem(TOKEN_KEY);
}

export const authHttp = axios.create({
  baseURL: BASE_URL,
  withCredentials: false,
});

authHttp.interceptors.request.use((cfg) => {
  const t = getToken();
  if (t) {
    cfg.headers = { ...(cfg.headers || {}), Authorization: `Bearer ${t}` };
  }
  return cfg;
});

// ====== AUTH API ======

export async function login(username: string, password: string) {
  // OAuth2PasswordRequestForm: ТОЛЬКО form-urlencoded
  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);
  const { data } = await authHttp.post(`${BASE_URL}/auth/login`, body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  if (data?.access_token) setToken(data.access_token);
  return data as { access_token: string; token_type: string };
}

export async function me() {
  const { data } = await authHttp.get(`${BASE_URL}/auth/me`);
  return data as {
    id: number;
    username: string;
    role: "super" | "promoter";
    full_name?: string | null;
  };
}

export async function createInvite(body: {
  role: "promoter" | "super";
  username: string;
  full_name?: string;
  store_id?: number;
  network?: string;
  expires_hours?: number; // по умолчанию 72
}) {
  const { data } = await authHttp.post(`${BASE_URL}/auth/invites`, body);
  return data as { code: string; username: string; role: string; expires_at: string };
}

export async function checkInvite(code: string) {
  const { data } = await authHttp.get(
    `${BASE_URL}/auth/invites/${encodeURIComponent(code)}`
  );
  return data as
    | {
        valid: true;
        username: string;
        role: "promoter" | "super";
        full_name?: string | null;
        store_id?: number | null;
        network?: string | null;
        expires_at?: string;
      }
    | { valid: false; reason?: "expired" | "used" | "not_found" };
}

export async function registerByInvite(code: string, password: string, full_name?: string) {
  const { data } = await authHttp.post(`${BASE_URL}/auth/register`, {
    code,
    password,
    full_name,
  });
  if (data?.access_token) setToken(data.access_token);
  return data as { access_token: string; token_type: string };
}

export function logout() {
  setToken(null);
}
