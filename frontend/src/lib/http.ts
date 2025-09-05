import axios from 'axios';

// Base URL from environment
const API_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';

// In-memory token storage
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

// Axios instance
const http = axios.create({
  baseURL: API_URL + '/api/v1',
  withCredentials: true,
});

// Attach Authorization header
http.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Handle refresh token logic
http.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401 && refreshToken) {
      try {
        const { data } = await axios.post(
          API_URL + '/api/v1/auth/refresh',
          { refresh_token: refreshToken }
        );
        setAuthTokens(data.access_token, data.refresh_token);
        localStorage.setItem('accessToken', data.access_token);
        localStorage.setItem('refreshToken', data.refresh_token);
        error.config.headers.Authorization = `Bearer ${data.access_token}`;
        return http(error.config);
      } catch (err) {
        clearAuthTokens();
      }
    }
    return Promise.reject(error);
  }
);

export default http;
