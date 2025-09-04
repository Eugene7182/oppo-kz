import { Navigate, useLocation } from 'react-router-dom'

function isAuthed() {
  return !!localStorage.getItem('access_token')
}

export default function RequireAuth({ children }: { children: JSX.Element }) {
  const location = useLocation()
  if (!isAuthed()) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}
