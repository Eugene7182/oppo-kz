import { FormEvent, useMemo, useState } from 'react'
import { http } from '../shared/http'

/**
 * InviteRecord описывает ответ API по созданию инвайта.
 * Приводим имена полей к camelCase, чтобы удобнее использовать в React.
 */
type InviteRecord = {
  code: string
  email: string
  role: 'admin' | 'office' | 'supervisor' | 'promoter'
  fullName?: string | null
  expiresAt: string
}

const roleOptions: Array<{ value: InviteRecord['role']; label: string; hint: string }> = [
  { value: 'promoter', label: 'Промоутер', hint: 'Доступ к ежедневным отчётам и бонусам' },
  { value: 'supervisor', label: 'Супервизор', hint: 'Региональная аналитика и коммуникации' },
  { value: 'office', label: 'Офис', hint: 'Планирование, бонусная сетка, сообщения' },
  { value: 'admin', label: 'Администратор', hint: 'Полный доступ (использовать осторожно)' },
]

const expiryOptions: Array<{ hours: number; label: string }> = [
  { hours: 24, label: '24 часа' },
  { hours: 72, label: '3 дня' },
  { hours: 168, label: '7 дней' },
  { hours: 336, label: '14 дней' },
]

/**
 * Возвращает ссылку для регистрации по инвайту.
 */
function buildInviteUrl(code: string): string {
  if (typeof window === 'undefined') return `/register/${code}`
  const origin = window.location.origin.replace(/\/$/, '')
  return `${origin}/register/${code}`
}

/**
 * Приводим ISO-дату к локальному формату без лишних деталей.
 */
function formatExpiresAt(value: string): string {
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return value
  return dt.toLocaleString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Страница управления инвайтами (admin/office).
 * Позволяет выпускать ссылки для регистрации и отслеживать последние созданные приглашения.
 */
export default function InvitesPage() {
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState<InviteRecord['role']>('promoter')
  const [expiresHours, setExpiresHours] = useState<number>(72)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [recent, setRecent] = useState<InviteRecord | null>(null)
  const [history, setHistory] = useState<InviteRecord[]>([])

  const inviteUrl = useMemo(() => (recent ? buildInviteUrl(recent.code) : ''), [recent])

  async function handleSubmit(evt: FormEvent<HTMLFormElement>) {
    evt.preventDefault()
    setError(null)

    if (!email.trim()) {
      setError('Укажите email получателя')
      return
    }

    setLoading(true)
    try {
      const payload = {
        email: email.trim(),
        role,
        full_name: fullName.trim() || undefined,
        expires_hours: expiresHours,
      }
      const { data } = await http.post('/api/v1/auth/invites', payload)
      const normalized: InviteRecord = {
        code: data.code,
        email: data.email,
        role: data.role,
        fullName: data.full_name ?? null,
        expiresAt: data.expires_at,
      }
      setRecent(normalized)
      setHistory((prev) => [normalized, ...prev].slice(0, 10))
      setEmail('')
      setFullName('')
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || 'Не удалось создать инвайт'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  async function copyInvite() {
    if (!inviteUrl) return
    try {
      await navigator.clipboard.writeText(inviteUrl)
      alert('Ссылка скопирована в буфер обмена')
    } catch (err) {
      console.warn('Clipboard error', err)
      alert(inviteUrl)
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 720, margin: '0 auto' }}>
      <h1 style={{ fontSize: 24, marginBottom: 12 }}>Инвайты пользователей</h1>
      <p style={{ marginBottom: 24, color: '#4b5563' }}>
        Выпускайте приглашения для сотрудников. Получатель перейдёт по ссылке, задаст пароль и войдёт в систему.
      </p>

      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 16, background: '#111827', color: '#f9fafb', padding: 20, borderRadius: 12 }}>
        <div style={{ display: 'grid', gap: 6 }}>
          <label htmlFor="invite-email">Email сотрудника</label>
          <input
            id="invite-email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="user@oppo.kz"
            style={{ padding: '10px 12px', borderRadius: 8, border: '1px solid #374151', color: '#111827' }}
          />
        </div>

        <div style={{ display: 'grid', gap: 6 }}>
          <label htmlFor="invite-name">ФИО (опционально)</label>
          <input
            id="invite-name"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Иванова Алия"
            style={{ padding: '10px 12px', borderRadius: 8, border: '1px solid #374151', color: '#111827' }}
          />
        </div>

        <div style={{ display: 'grid', gap: 6 }}>
          <label htmlFor="invite-role">Роль</label>
          <select
            id="invite-role"
            value={role}
            onChange={(e) => setRole(e.target.value as InviteRecord['role'])}
            style={{ padding: '10px 12px', borderRadius: 8, border: '1px solid #374151', color: '#111827' }}
          >
            {roleOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <small style={{ color: '#d1d5db' }}>{roleOptions.find((opt) => opt.value === role)?.hint}</small>
        </div>

        <div style={{ display: 'grid', gap: 6 }}>
          <label htmlFor="invite-expiry">Срок действия</label>
          <select
            id="invite-expiry"
            value={expiresHours}
            onChange={(e) => setExpiresHours(Number(e.target.value))}
            style={{ padding: '10px 12px', borderRadius: 8, border: '1px solid #374151', color: '#111827' }}
          >
            {expiryOptions.map((opt) => (
              <option key={opt.hours} value={opt.hours}>
                {opt.label}
              </option>
            ))}
          </select>
          <small style={{ color: '#d1d5db' }}>После истечения срока ссылка автоматически перестанет работать.</small>
        </div>

        {error && <div style={{ color: '#fca5a5' }}>{error}</div>}

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '12px 16px',
            borderRadius: 8,
            border: 'none',
            fontWeight: 600,
            background: loading ? '#9ca3af' : '#22d3ee',
            color: '#0f172a',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'background 0.2s ease',
          }}
        >
          {loading ? 'Создаём…' : 'Создать инвайт'}
        </button>
      </form>

      {recent && (
        <section style={{ marginTop: 32, padding: 20, border: '1px solid #e5e7eb', borderRadius: 12 }}>
          <h2 style={{ fontSize: 20, marginBottom: 12 }}>Ссылка готова</h2>
          <p style={{ marginBottom: 12 }}>
            Передайте ссылку сотруднику. После регистрации инвайт автоматически пометится использованным.
          </p>
          <div style={{ display: 'grid', gap: 8, wordBreak: 'break-all' }}>
            <div><strong>Email:</strong> {recent.email}</div>
            {recent.fullName && <div><strong>ФИО:</strong> {recent.fullName}</div>}
            <div><strong>Роль:</strong> {roleOptions.find((opt) => opt.value === recent.role)?.label ?? recent.role}</div>
            <div><strong>Действителен до:</strong> {formatExpiresAt(recent.expiresAt)}</div>
            <div><strong>Ссылка:</strong> {inviteUrl}</div>
          </div>
          <button
            type="button"
            onClick={copyInvite}
            style={{
              marginTop: 16,
              padding: '10px 14px',
              borderRadius: 8,
              border: '1px solid #0ea5e9',
              background: '#e0f2fe',
              color: '#0c4a6e',
              cursor: 'pointer',
            }}
          >
            Скопировать ссылку
          </button>
        </section>
      )}

      {history.length > 0 && (
        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: 18, marginBottom: 12 }}>Последние выпущенные инвайты</h2>
          <div style={{ border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead style={{ background: '#f9fafb', textAlign: 'left' }}>
                <tr>
                  <th style={{ padding: '10px 12px', borderBottom: '1px solid #e5e7eb' }}>Email</th>
                  <th style={{ padding: '10px 12px', borderBottom: '1px solid #e5e7eb' }}>Роль</th>
                  <th style={{ padding: '10px 12px', borderBottom: '1px solid #e5e7eb' }}>Действует до</th>
                  <th style={{ padding: '10px 12px', borderBottom: '1px solid #e5e7eb' }}>Код</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.code}>
                    <td style={{ padding: '10px 12px', borderBottom: '1px solid #f3f4f6' }}>{item.email}</td>
                    <td style={{ padding: '10px 12px', borderBottom: '1px solid #f3f4f6' }}>
                      {roleOptions.find((opt) => opt.value === item.role)?.label ?? item.role}
                    </td>
                    <td style={{ padding: '10px 12px', borderBottom: '1px solid #f3f4f6' }}>{formatExpiresAt(item.expiresAt)}</td>
                    <td style={{ padding: '10px 12px', borderBottom: '1px solid #f3f4f6', fontFamily: 'monospace' }}>{item.code}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}
