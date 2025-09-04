// frontend/src/pages/Login.tsx
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { login, me } from '../services/auth';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation() as any;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();               // ← это и есть обработчик submit
    setError(null);
    setLoading(true);
    try {
      await login(username, password); // сохраняет access_token
      await me().catch(() => {});
      const to = location.state?.from?.pathname || '/';
      navigate(to, { replace: true });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Ошибка входа';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 480, margin: '48px auto', padding: 16 }}>
      <h1>Вход</h1>
      <p>Введите логин и пароль. Логин = <i>username</i> из инвайта (можно e-mail).</p>
      <form onSubmit={onSubmit}>
        <label>Логин</label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="email или username"
          style={{ width: '100%', padding: 8, marginBottom: 12 }}
        />
        <label>Пароль</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          style={{ width: '100%', padding: 8, marginBottom: 12 }}
        />
        {error && <div style={{ color: 'red', marginBottom: 8 }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ width: '100%', padding: 10 }}>
          {loading ? 'Входим…' : 'Войти'}
        </button>
      </form>
      <div style={{ marginTop: 12 }}>
        <a href="/">← На главную</a>
      </div>
    </div>
  );
}
