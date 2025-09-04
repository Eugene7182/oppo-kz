// Единый HTTP-клиент с валидацией URL и автоподстановкой Bearer токена.
import axios from 'axios'

const raw = (import.meta.env.VITE_API_URL ?? '').trim()

if (!/^https?:\/\//i.test(raw)) {
  throw new Error(`VITE_API_URL must start with http(s)://, got "${raw || '<empty>'}"`)
}

export const http = axios.create({
  baseURL: raw.replace(/\/+$/, ''), // без trailing slash
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (r) => r,
  (err) => {
    // Дадим понятный текст вместо «Network Error»
    if (!err.response) {
      err.message = 'Сетевая ошибка или CORS-блокировка. Проверь CORS_ORIGINS и VITE_API_URL.'
    }
    return Promise.reject(err)
  }
)
