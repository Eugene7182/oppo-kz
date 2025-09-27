// frontend/src/shared/http.ts
import axios from 'axios'

const rawEnv = (import.meta.env.VITE_API_URL ?? '').trim()
let base = rawEnv

// Если env кривой — используем безопасный фолбэк и не валим приложение.
if (!/^https?:\/\//i.test(base)) {
  console.warn(
    `[HTTP] VITE_API_URL invalid or empty ("${rawEnv || '<empty>'}"). ` +
    `Falling back to https://oppo-kz.onrender.com`
  )
  base = 'https://oppo-kz.onrender.com'
}

// Уберём хвостовой слэш
base = base.replace(/\/+$/, '')

export const http = axios.create({
  baseURL: base,
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
    if (!err.response) {
      err.message = 'Сетевая ошибка или CORS. Проверь CORS_ORIGINS и VITE_API_URL.'
    }
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      const back = encodeURIComponent(location.pathname + location.search)
      location.assign(`/login?back=${back}`)
    }
    return Promise.reject(err)
  }
)

export function getApiBase() {
  return base
}
