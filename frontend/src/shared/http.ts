// frontend/src/shared/http.ts
import axios from 'axios';

const raw = (import.meta.env.VITE_API_URL ?? '').trim();
if (!/^https?:\/\//i.test(raw)) {
  throw new Error(`VITE_API_URL must start with http(s)://, got "${raw || '<empty>'}"`);
}

export const http = axios.create({
  baseURL: raw.replace(/\/+$/, ''), // без трейлинга '/'
  timeout: 15000,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

http.interceptors.response.use(
  (r) => r,
  (err) => {
    if (!err.response) {
      err.message = 'Сетевая ошибка или CORS. Проверь CORS_ORIGINS и VITE_API_URL.';
    }
    return Promise.reject(err);
  }
);
