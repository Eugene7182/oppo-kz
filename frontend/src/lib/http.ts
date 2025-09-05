import axios from 'axios';
import { toast } from './toast';

// Базовый URL из окружения
const API_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';

// Токены храним в памяти и в localStorage
let accessToken = localStorage.getItem('accessToken') || '';
let refreshToken = localStorage.getItem('refreshToken') || '';

export const setAuthTokens = (access: string, refresh: string) => {
  accessToken = access;
  refreshToken = refresh;
};

export const clearAuthTokens = () => {
  accessToken = '';
  refreshToken = '';
};

// Создаём axios-инстанс
const http = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Перед каждым запросом добавляем заголовок Authorization
http.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Обработка ответов и обновление токена при 401
http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && refreshToken && !original._retry) {
      original._retry = true;
      try {
        const { data } = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });
        setAuthTokens(data.access_token, data.refresh_token);
        localStorage.setItem('accessToken', data.access_token);
        localStorage.setItem('refreshToken', data.refresh_token);
        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return http(original); // повторяем исходный запрос один раз
      } catch (err) {
        clearAuthTokens();
      }
    }
    const message = error.response?.data?.detail || error.message;
    console.error('HTTP error:', message, error);
    toast(message || 'Ошибка запроса', 'error');
    return Promise.reject(error);
  },
);

export default http;
