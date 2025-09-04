
import { useEffect, useState } from 'react'
import { http } from '../shared/http'
import DataTable from '../components/DataTable'

export default function InventoryPage() {
  const [items, setItems] = useState<any[]>([])
  const [filters, setFilters] = useState({ store_id:'', sku_id:'' })
  const [form, setForm] = useState({ store_id:'', sku_id:'', on_hand:'', in_transit:'' })
  const [err, setErr] = useState<string | null>(null)

  async function load() {
    const params: any = {}
    if (filters.store_id) params.store_id = Number(filters.store_id)
    if (filters.sku_id) params.sku_id = Number(filters.sku_id)
    const { data } = await http.get('/api/v1/inventory', { params })
    setItems(data.items)
  }
  useEffect(()=>{ load() }, [filters.store_id, filters.sku_id])

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setErr(null)
    try {
      const payload = {
        store_id: Number(form.store_id),
        sku_id: Number(form.sku_id),
        on_hand: Number(form.on_hand || 0),
        in_transit: Number(form.in_transit || 0),
      }
      await http.post('/api/v1/inventory/upsert', payload)
      setForm({ store_id:'', sku_id:'', on_hand:'', in_transit:'' })
      load()
    } catch (e:any) {
      setErr(e?.response?.data?.detail || e?.message || 'Ошибка')
    }
  }

  async function del_(id: number) {
    if (!confirm('Удалить запись?')) return
    await http.delete('/api/v1/inventory/' + id)
    load()
  }

  return (
    <div>
      <h2>Остатки и транзит</h2>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:8, marginBottom:12 }}>
        <input placeholder="Store ID" value={filters.store_id} onChange={e=>setFilters({ ...filters, store_id: e.target.value })} />
        <input placeholder="SKU ID" value={filters.sku_id} onChange={e=>setFilters({ ...filters, sku_id: e.target.value })} />
      </div>

      <form onSubmit={submit} style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:8, marginBottom:12 }}>
        <input placeholder="Store ID" value={form.store_id} onChange={e=>setForm({ ...form, store_id: e.target.value })} required />
        <input placeholder="SKU ID" value={form.sku_id} onChange={e=>setForm({ ...form, sku_id: e.target.value })} required />
        <input placeholder="On hand" value={form.on_hand} onChange={e=>setForm({ ...form, on_hand: e.target.value })} />
        <input placeholder="In transit" value={form.in_transit} onChange={e=>setForm({ ...form, in_transit: e.target.value })} />
        <div style={{ gridColumn:'1 / -1' }}>
          <button type="submit">Сохранить</button>
          {err && <span style={{ color:'crimson', marginLeft:12 }}>{err}</span>}
        </div>
      </form>

      <DataTable rows={items} columns={[
        { key:'id', title:'ID' },
        { key:'store_id', title:'Store' },
        { key:'sku_id', title:'SKU' },
        { key:'on_hand', title:'On hand' },
        { key:'in_transit', title:'In transit' },
      ]}/>

      <ul>
        {items.map(i => (<li key={i.id}>#{i.id} <button onClick={()=>del_(i.id)}>Удалить</button></li>))}
      </ul>
    </div>
  )
}
