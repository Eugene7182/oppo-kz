import { useEffect, useState } from 'react';
import { me } from '../services/auth';

// Асинхронная проверка ролей через /auth/me
export default function RequireRole({
  roles,
  children,
}: {
  roles: string[];
  children: JSX.Element;
}) {
  const [allowed, setAllowed] = useState<null | boolean>(null);

  useEffect(() => {
    me()
      .then((u) => setAllowed(roles.includes((u.role || '').toLowerCase())))
      .catch(() => setAllowed(false));
  }, [roles]);

  if (allowed === null) return <div>Проверяем доступ…</div>;
  if (!allowed) return <div style={{ color: 'crimson' }}>403 Forbidden: нет прав</div>;
  return children;
}
