// frontend/src/pages/InviteRegister.tsx
import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { http } from '../shared/http'

type InviteCheck = {
  email: string
  full_name?: string
  role: string
  used: boolean
  expired: boolean
}

export default function InviteRegisterPage() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const [info, setInfo] = useState<InviteCheck | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!code) return
    http.get(`/api/v1/auth/invites/${code}`)
      .then(r => setInfo(r.data))
      .catch(e => setError(e?.response?.data?.detail || 'Инвайт не найден'))
  }, [code])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (password.length < 8) { setError('Пароль должен быть не короче 8 символов'); return }
    if (password !== confirm) { setError('Пароли не совпадают'); return }
    setLoading(true)
    try {
      await http.post('/api/v1/auth/invites/register', { code, password })
      alert('Аккаунт создан! Теперь войдите под своим email и паролем.')
      navigate('/login', { replace: true })
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Не удалось завершить регистрацию')
    } finally {
      setLoading(false)
    }
  }

  if (!code) return <div>Некорректная ссылка</div>
  if (error) return <div style={{ color: 'crimson' }}>{error}</div>
  if (!info) return <div>Проверяем инвайт…</div>
  if (info.used) return <div>Инвайт уже использован.</div>
  if (info.expired) return <div>Инвайт истёк.</div>

  return (
    <div style={{ maxWidth: 520, margin: '48px auto', padding: 16 }}>
      <h2>Регистрация по инвайту</h2>
      <p><b>Email:</b> {info.email} · <b>Роль:</b> {info.role}</p>
      <form onSubmit={onSubmit}>
        <label>Пароль</label>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          style={{ width: '100%', padding: 8, marginBottom: 12 }}
          placeholder="Не менее 8 символов"
        />
        <label>Повторите пароль</label>
        <input
          type="password"
          value={confirm}
          onChange={e => setConfirm(e.target.value)}
          style={{ width: '100%', padding: 8, marginBottom: 12 }}
        />
        {error && <div style={{ color: 'crimson', marginBottom: 8 }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ padding: '10px 14px' }}>
          {loading ? 'Создаём…' : 'Завершить регистрацию'}
        </button>
      </form>
    </div>
  )
}
