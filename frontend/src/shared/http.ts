import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL as string
if (!API_URL) throw new Error('VITE_API_URL is not set')

export const http = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  withCredentials: false,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (r) => r,
  (err) => {
    // TODO: показать toast/уведомление, или редирект на /login при 401
    return Promise.reject(err)
  }
)
