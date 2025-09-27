import React, { useEffect, useState } from 'react';
import { fetchOfficeSummary, fetchOfficeWeeklyVs, fetchOfficeProjection } from '../shared/api/office';
import { api } from '../shared/api/http';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, LineChart, Line } from 'recharts';

export default function OfficeDashboard(){
  const [scope, setScope] = useState<'today'|'yesterday'|'week'|'month'>('week');
  const [sum, setSum] = useState<any>(null);
  const [wvs, setWvs] = useState<any>(null);
  const [proj, setProj] = useState<any>(null);
  const [topModels, setTopModels] = useState<any[]>([]);
  const [topStores, setTopStores] = useState<any[]>([]);

  const load = async () => {
    const s = await fetchOfficeSummary({ scope }); setSum(s);
    const w = await fetchOfficeWeeklyVs({ weeks: 12 }); setWvs(w);
    const p = await fetchOfficeProjection({}); setProj(p);
    const m = await api.get('/api/v1/office/top/models', { params: { limit: 15 } }); setTopModels(m.data.rows || []);
    const st = await api.get('/api/v1/office/top/stores', { params: { limit: 15 } }); setTopStores(st.data.rows || []);
  };
  useEffect(()=>{ load(); }, [scope]);

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-semibold">Офис — Дашборд</h2>
      <div className="flex gap-2 items-end">
        <select className="border rounded px-2 py-1" value={scope} onChange={e=>setScope(e.target.value as any)}>
          <option value="today">Сегодня</option><option value="yesterday">Вчера</option>
          <option value="week">Неделя</option><option value="month">Месяц</option>
        </select>
        <button className="px-3 py-2 rounded bg-gray-800 text-white" onClick={load}>Обновить</button>
      </div>

      {sum && (
        <div className="grid md:grid-cols-3 gap-3">
          <div className="p-3 border rounded">Total Qty: <b>{Math.round(sum.total.qty||0)}</b></div>
          <div className="p-3 border rounded">Total Revenue: <b>{Math.round(sum.total.revenue||0)}</b></div>
          <div className="p-3 border rounded">Период: {sum.period.from||'-'} — {sum.period.to||'-'}</div>
        </div>
      )}

      {wvs && (
        <div className="p-3 border rounded">
          <div className="font-medium mb-2">Недели (Qty)</div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={wvs.weeks}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="qty" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {proj && (
        <div className="grid md:grid-cols-2 gap-3">
          <div className="p-3 border rounded">
            <div className="font-medium mb-2">Проекция на месяц (Qty)</div>
            <div>MTD: <b>{Math.round(proj.mtd_qty)}</b> / Run-rate: <b>{proj.runrate_qty.toFixed(1)}</b> / EOM: <b>{proj.eom_qty.toFixed(0)}</b></div>
          </div>
          <div className="p-3 border rounded">
            <div className="font-medium mb-2">Проекция на месяц (Revenue)</div>
            <div>MTD: <b>{Math.round(proj.mtd_revenue)}</b> / Run-rate: <b>{proj.runrate_revenue.toFixed(1)}</b> / EOM: <b>{proj.eom_revenue.toFixed(0)}</b></div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-3">
        <div className="p-3 border rounded">
          <div className="font-medium mb-2">Топ моделей</div>
          <div className="overflow-auto">
            <table className="min-w-[400px] text-sm">
              <thead><tr className="bg-gray-50"><th className="p-2">Модель</th><th className="p-2">Qty</th></tr></thead>
              <tbody>{topModels.map((r:any,idx:number)=>(<tr key={idx} className="border-t"><td className="p-1">{r.model}</td><td className="p-1">{Math.round(r.qty)}</td></tr>))}</tbody>
            </table>
          </div>
        </div>
        <div className="p-3 border rounded">
          <div className="font-medium mb-2">Топ магазинов</div>
          <div className="overflow-auto">
            <table className="min-w-[400px] text-sm">
              <thead><tr className="bg-gray-50"><th className="p-2">Store</th><th className="p-2">Qty</th></tr></thead>
              <tbody>{topStores.map((r:any,idx:number)=>(<tr key={idx} className="border-t"><td className="p-1">{r.store_id}</td><td className="p-1">{Math.round(r.qty)}</td></tr>))}</tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
