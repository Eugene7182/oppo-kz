import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logout, me, Me } from '../services/auth';

export default function Layout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    me().then(setUser).catch(() => setUser(null));
  }, []);

  return (
    <div>
      <header style={{ padding: '12px 16px', borderBottom: '1px solid #eee', display: 'flex', gap: 16, alignItems: 'center' }}>
        <Link to="/">Dashboard</Link>
        <Link to="/invites">Инвайты</Link>
        <div style={{ marginLeft: 'auto', opacity: 0.8 }}>
          {user ? (
            <>
              <span style={{ marginRight: 12 }}>{user.full_name || user.email} ({user.role})</span>
              <button
                onClick={() => { logout(); navigate('/login', { replace: true }); }}
              >
                Выйти
              </button>
            </>
          ) : (
            <Link to="/login">Войти</Link>
          )}
        </div>
      </header>
      <main style={{ padding: 24 }}>{children}</main>
    </div>
  );
}
