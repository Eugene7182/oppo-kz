import { useEffect, useState } from 'react'
import { me } from '../services/auth'

// Асинхронная проверка ролей через /auth/me.
// Показывает "403 Forbidden", если роль не входит в список.
export default function RequireRole({
  roles,
  children,
}: {
  roles: string[]
  children: JSX.Element
}) {
  const [allowed, setAllowed] = useState<null | boolean>(null)

  useEffect(() => {
    me()
      .then((u) => {
        const role = (u.role || '').toLowerCase()
        setAllowed(roles.map(r => r.toLowerCase()).includes(role))
      })
      .catch(() => setAllowed(false))
  }, [roles])

  if (allowed === null) return <div>Проверяем доступ…</div>
  if (!allowed) return <div style={{ color: 'crimson' }}>403 Forbidden: нет прав</div>
  return children
}
