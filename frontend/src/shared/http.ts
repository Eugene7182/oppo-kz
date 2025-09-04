// frontend/src/shared/http.ts
import axios from 'axios';

const raw = (import.meta.env.VITE_API_URL ?? '').trim();
if (!/^https?:\/\//i.test(raw)) {
  throw new Error(`VITE_API_URL must start with http(s)://, got "${raw || '<empty>'}"`);
}

export const http = axios.create({
  baseURL: raw.replace(/\/+$/, ''), // убираем хвостовой "/"
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
    // Покажем понятное сообщение вместо "Network Error"
    if (!err.response) {
      err.message = 'Сетевая ошибка или CORS. Проверь CORS_ORIGINS и VITE_API_URL.';
    }
    // Если истек токен/невалиден — выходим на /login
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Сохраним адрес, чтобы вернуться после логина
      const back = encodeURIComponent(location.pathname + location.search);
      location.assign(`/login?back=${back}`);
    }
    return Promise.reject(err);
  }
);
