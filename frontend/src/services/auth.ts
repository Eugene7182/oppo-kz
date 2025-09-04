// frontend/src/services/auth.ts
import { http } from '../shared/http';

type LoginResp = {
  access_token?: string;
  token?: string;
  jwt?: string;
  token_type?: string;
};

export async function login(username: string, password: string) {
  const { data } = await http.post<LoginResp>('/api/v1/auth/login', { username, password });
  const token = data.access_token || data.token || data.jwt;
  if (!token) throw new Error('Не удалось получить токен. Ответ: ' + JSON.stringify(data));
  localStorage.setItem('access_token', token);
  return data;
}

export async function me() {
  const { data } = await http.get('/api/v1/auth/me');
  return data;
}

export function logout() {
  localStorage.removeItem('access_token');
}
