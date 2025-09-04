
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { me, logout } from '../services/auth'
import type { Me } from '../services/auth'

export default function Layout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Me | null>(null)
  const navigate = useNavigate()
  useEffect(()=>{ me().then(setUser).catch(()=>setUser(null)) },[])
  return (
    <div>
      <header style={{ padding:'12px 16px', borderBottom:'1px solid #eee', display:'flex', gap:16, flexWrap:'wrap' }}>
        <Link to="/">Dashboard</Link>
        <Link to="/stores">Магазины</Link>
        <Link to="/sku">SKU</Link>
        <Link to="/invites">Инвайты</Link>
        <Link to="/sales">Продажи</Link>
        <Link to="/price-list">Прайс</Link>
        <Link to="/coeffs">Коэфф.</Link>
        <Link to="/bonus">Бонусы</Link>
        <Link to="/imports">Импорты</Link>
        <Link to="/moves">Перемещения</Link>
        <Link to="/inventory">Остатки</Link>
        <Link to="/reconciliation">Сверка</Link>
        <div style={{ marginLeft:'auto' }}>
          {user ? (<>
            <span style={{ marginRight:12 }}>{user.full_name || user.email} ({user.role})</span>
            <button onClick={()=>{ logout(); navigate('/login', { replace:true }) }}>Выйти</button>
          </>) : <Link to="/login">Войти</Link>}
        </div>
      </header>
      <main style={{ padding:24 }}>{children}</main>
    </div>
  )
}
