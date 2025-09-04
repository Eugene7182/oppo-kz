import { useEffect, useState } from 'react';
import { me, Me } from '../services/auth';

export default function Dashboard() {
  const [user, setUser] = useState<Me | null>(null);
  useEffect(() => { me().then(setUser).catch(() => setUser(null)); }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Вы авторизованы.</p>
      {user && (
        <ul>
          <li><b>Email:</b> {user.email}</li>
          <li><b>Имя:</b> {user.full_name || '—'}</li>
          <li><b>Роль:</b> {user.role}</li>
        </ul>
      )}
    </div>
  );
}
