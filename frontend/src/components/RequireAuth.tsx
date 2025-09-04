// frontend/src/components/RequireAuth.tsx
// Простой токен-гард: если нет access_token — уводим на /login.
import { Navigate, useLocation } from 'react-router-dom'

export default function RequireAuth({ children }: { children: JSX.Element }) {
  const location = useLocation()
  const token =
    typeof window !== 'undefined' ? localStorage.getItem('access_token') : null

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return children
}
