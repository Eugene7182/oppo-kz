import React, { useEffect, useState } from 'react';
import { listSales, upsertSale, deleteSale } from '../shared/api/sales_edit';
import { api } from '../shared/api/http';

function firstDayOfMonthISO(d=new Date()){ return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0,10); }

export default function SalesEditor(){
  const [dateISO, setDateISO] = useState<string>(new Date().toISOString().slice(0,10));
  const [store, setStore] = useState<string>('');
  const [promoter, setPromoter] = useState<string>('');
  const [skus, setSkus] = useState<{sku_id:string; model:string}[]>([]);
  const [rows, setRows] = useState<any[]>([]);
  const [form, setForm] = useState<any>({ sku_id:'', model:'', memory_gb:128, qty:0, price_per_unit:0, network_id:'' });
  const [msg, setMsg] = useState<string>('');

  useEffect(()=>{ api.get('/api/v1/skus').then(r=>setSkus(r.data.items||[])).catch(()=>{}); }, []);

  const load = async () => {
    const r = await listSales({ date: dateISO, store_id: store || undefined, promoter_username: promoter || undefined });
    setRows(r.rows || []);
  };
  useEffect(()=>{ load(); }, [dateISO, store, promoter]);

  const save = async () => {
    if (!store || !form.sku_id){ setMsg('Store и SKU обязательны'); return; }
    await upsertSale({ date: dateISO, store_id: store, sku_id: form.sku_id, model: form.model, memory_gb: Number(form.memory_gb||0), qty: Number(form.qty||0), price_per_unit: Number(form.price_per_unit||0), network_id: form.network_id || undefined, promoter_username: promoter || undefined });
    setMsg('Сохранено'); await load();
  };
  const del = async (r:any) => {
    await deleteSale({ date: r.date, store_id: r.store_id, sku_id: r.sku_id, memory_gb: r.memory_gb ?? undefined, promoter_username: r.promoter || undefined });
    await load();
  };

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">Редактор продаж (текущий месяц)</h2>
      <div className="grid md:grid-cols-4 gap-2">
        <div><div className="text-xs opacity-60">Дата</div><input type="date" className="border rounded px-2 py-1 w-full" value={dateISO} onChange={e=>setDateISO(e.target.value)} /></div>
        <div><div className="text-xs opacity-60">Магазин</div><input className="border rounded px-2 py-1 w-full" value={store} onChange={e=>setStore(e.target.value)} placeholder="STORE_ID"/></div>
        <div><div className="text-xs opacity-60">Промоутер (опц. для супервайзера)</div><input className="border rounded px-2 py-1 w-full" value={promoter} onChange={e=>setPromoter(e.target.value)} placeholder="username"/></div>
      </div>

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Добавить/изменить строку</div>
        <div className="grid md:grid-cols-6 gap-2">
          <select className="border rounded px-2 py-1" value={form.sku_id} onChange={e=>{ 
            const sku = e.target.value;
            setForm((f:any)=>({ ...f, sku_id: sku, model: (skus.find(s=>s.sku_id===sku)?.model || '') }));
          }}>
            <option value="">— SKU —</option>
            {skus.map(s=>(<option key={s.sku_id} value={s.sku_id}>{s.model}</option>))}
          </select>
          <input type="number" className="border rounded px-2 py-1" placeholder="Память (GB)" value={form.memory_gb} onChange={e=>setForm((f:any)=>({ ...f, memory_gb: Number(e.target.value||0) }))}/>
          <input type="number" className="border rounded px-2 py-1" placeholder="Qty" value={form.qty} onChange={e=>setForm((f:any)=>({ ...f, qty: Number(e.target.value||0) }))}/>
          <input type="number" className="border rounded px-2 py-1" placeholder="Цена/шт" value={form.price_per_unit} onChange={e=>setForm((f:any)=>({ ...f, price_per_unit: Number(e.target.value||0) }))}/>
          <input className="border rounded px-2 py-1" placeholder="Сеть (опц.)" value={form.network_id} onChange={e=>setForm((f:any)=>({ ...f, network_id: e.target.value }))}/>
          <button className="px-3 py-1 rounded bg-green-600 text-white" onClick={save}>Сохранить</button>
        </div>
        {msg && <div className="text-sm mt-1">{msg}</div>}
      </div>

      <div className="p-3 border rounded overflow-auto">
        <div className="font-medium mb-2">Строки за день</div>
        <table className="min-w-[900px] text-sm">
          <thead>
            <tr className="bg-gray-50">
              <th className="p-2">Store</th><th className="p-2">SKU</th><th className="p-2">Model</th><th className="p-2">Mem</th><th className="p-2">Qty</th><th className="p-2">Revenue</th><th className="p-2">Promoter</th><th className="p-2"></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r,idx)=>(
              <tr key={idx} className="border-t">
                <td className="p-1">{r.store_id}</td>
                <td className="p-1">{r.sku_id}</td>
                <td className="p-1">{r.model}</td>
                <td className="p-1">{r.memory_gb ?? '-'}</td>
                <td className="p-1">{r.qty}</td>
                <td className="p-1">{r.revenue ?? '-'}</td>
                <td className="p-1">{r.promoter || '-'}</td>
                <td className="p-1"><button className="px-2 py-1 rounded bg-red-600 text-white" onClick={()=>del(r)}>Удалить</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
