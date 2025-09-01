import React, { useEffect, useState } from 'react';
import { fetchMeProfile } from '../shared/api/users';
import { superPlanReminder } from '../shared/api/reminders';
import { api } from '../shared/api/http';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function SupervisorDashboard(){
  const [city, setCity] = useState<string>('');
  const [scope, setScope] = useState<'today'|'yesterday'|'week'|'month'>('week');
  const [sum, setSum] = useState<any>(null);
  const [weeks, setWeeks] = useState<any[]>([]);
  const [top, setTop] = useState<any[]>([]);

  useEffect(()=>{
    fetchMeProfile().then(me=>{ if (me?.city_code) setCity(me.city_code); });
  }, []);

  const load = async () => {
    const s = await api.get('/api/v1/superdash/summary', { params: { scope, city } });
    setSum(s.data);
    const w = await api.get('/api/v1/superdash/weekly_vs', { params: { weeks: 10, city } });
    setWeeks(w.data.weeks || []);
    const t = await api.get('/api/v1/superdash/promoter_sales', { params: { group_by: 'model' } });
    setTop(t.data.rows || []);
  };
  useEffect(()=>{ load(); }, [scope, city]);
  const [planInfo, setPlanInfo] = useState<any>(null);
  const [showBanner, setShowBanner] = useState<boolean>(false);
  useEffect(()=>{
    const first = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0,10);
    const key = 'plan_banner_next_' + (city||'');
    const check = async () => {
      try{
        const d = await superPlanReminder({ city: city||undefined, month: first });
        setPlanInfo(d);
        const nextAt = localStorage.getItem(key);
        const now = Date.now();
        if (d.needs_plan) {
          if (!nextAt || now > Number(nextAt)) { setShowBanner(true); }
        } else {
          setShowBanner(false);
        }
      }catch{}
    };
    check();
  }, [city]);


  return (
    <div className="p-4 space-y-4">
      {showBanner && planInfo?.needs_plan && (
        <div className="p-3 border rounded bg-yellow-50">
          <div className="font-medium">Нужны планы на {planInfo.month} по городу {planInfo.city}. Магазинов без плана: {planInfo.missing_count}.</div>
          <div className="text-xs opacity-70">Напоминание будет повторяться каждые 3 дня, пока планы не установят.</div>
          <button className="mt-2 px-3 py-2 rounded bg-yellow-600 text-white" onClick={()=>{ const next=Date.now()+3*24*3600*1000; localStorage.setItem('plan_banner_next_'+(city||''), String(next)); setShowBanner(false); }}>Скрыть на 3 дня</button>
        </div>
      )}

      <h2 className="text-xl font-semibold">Дашборд супервайзера</h2>
      <div className="flex gap-2 items-end">
        <div><div className="text-xs opacity-60">Город</div><input className="border rounded px-2 py-1" value={city||''} onChange={e=>setCity(e.target.value)} placeholder="ALMATY"/></div>
        <div><div className="text-xs opacity-60">Период</div>
          <select className="border rounded px-2 py-1" value={scope} onChange={e=>setScope(e.target.value as any)}>
            <option value="today">Сегодня</option><option value="yesterday">Вчера</option>
            <option value="week">Неделя</option><option value="month">Месяц</option>
          </select>
        </div>
        <button className="px-3 py-2 rounded bg-gray-800 text-white" onClick={load}>Обновить</button>
      </div>

      {sum && (
        <div className="grid md:grid-cols-3 gap-3">
          <div className="p-3 border rounded">Qty: <b>{Math.round(sum.total.qty||0)}</b></div>
          <div className="p-3 border rounded">Revenue: <b>{Math.round(sum.total.revenue||0)}</b></div>
          <div className="p-3 border rounded">Город: <b>{city||'—'}</b></div>
        </div>
      )}

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Недели (Qty)</div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={weeks}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" /><YAxis /><Tooltip />
            <Line type="monotone" dataKey="qty" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Топ моделей (объём)</div>
        <div className="overflow-auto">
          <table className="min-w-[600px] text-sm">
            <thead><tr className="bg-gray-50"><th className="p-2">Модель</th><th className="p-2">Qty</th></tr></thead>
            <tbody>
              {top.map((r,idx)=>(<tr key={idx} className="border-t"><td className="p-1">{r.key}</td><td className="p-1">{Math.round(r.qty)}</td></tr>))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
