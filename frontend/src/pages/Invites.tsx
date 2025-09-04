import { useState } from 'react';
import { http } from '../shared/http';

type InviteCreateIn = {
  email: string;
  full_name: string;
  role: string;            // promoter | supervisor | office | admin
  expires_hours?: number;  // по умолчанию 72
};

export default function InvitesPage() {
  const [form, setForm] = useState<InviteCreateIn>({
    email: '',
    full_name: '',
    role: 'promoter',
    expires_hours: 72,
  });
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const { data } = await http.post('/api/v1/auth/invites', form);
      setResult(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Ошибка создания инвайта');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 620 }}>
      <h2>Создать инвайт</h2>
      <form onSubmit={onSubmit}>
        <label>Email*</label>
        <input
          required
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          style={{ width: '100%', padding: 8, marginBottom: 12 }}
        />

        <label>ФИО*</label>
        <input
          required
          value={form.full_name}
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
          style={{ width: '100%', padding: 8, marginBottom: 12 }}
        />

        <label>Роль*</label>
        <select
          value={form.role}
          onChange={(e) => setForm({ ...form, role: e.target.value })}
          style={{ width: '100%', padding: 8, marginBottom: 12 }}
        >
          <option value="promoter">promoter</option>
          <option value="supervisor">supervisor</option>
          <option value="office">office</option>
          <option value="admin">admin</option>
        </select>

        <label>Срок действия (часы)</label>
        <input
          type="number"
          min={1}
          value={form.expires_hours ?? 72}
          onChange={(e) => setForm({ ...form, expires_hours: Number(e.target.value) })}
          style={{ width: '100%', padding: 8, marginBottom: 12 }}
        />

        {error && <div style={{ color: 'crimson', marginBottom: 8 }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ padding: '10px 14px' }}>
          {loading ? 'Создаём…' : 'Создать инвайт'}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: 16 }}>
          <h3>Результат</h3>
          <pre style={{ background: '#111', color: '#eee', padding: 12, borderRadius: 8 }}>
{JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
