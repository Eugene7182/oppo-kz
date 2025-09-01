import React, { useEffect, useState } from 'react';
import { getPlansAll, setPlan } from '../shared/api/plans';

export default function OfficePlans(){
  const [month, setMonth] = useState<string>(new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0,10));
  const [rows, setRows] = useState<any[]>([]);
  const [storeId, setStoreId] = useState('');
  const [planQty, setPlanQty] = useState<number>(0);

  const load = async () => {
    const r = await getPlansAll({ month });
    setRows(r.rows || []);
  };
  useEffect(()=>{ load(); }, [month]);

  const save = async () => {
    if (!storeId || !month) return;
    await setPlan({ store_id: storeId, month, plan_qty: Number(planQty||0) });
    setStoreId(''); setPlanQty(0); await load();
  };

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">Планы по магазинам (вся сеть)</h2>
      <div className="flex gap-2 items-end">
        <div><div className="text-xs opacity-60">Месяц</div><input type="date" className="border rounded px-2 py-1" value={month} onChange={e=>setMonth(e.target.value)} /></div>
        <button className="px-3 py-2 rounded bg-gray-800 text-white" onClick={load}>Обновить</button>
      </div>

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Текущие планы</div>
        <div className="overflow-auto">
          <table className="min-w-[900px] text-sm">
            <thead><tr className="bg-gray-50"><th className="p-2">City</th><th className="p-2">Store</th><th className="p-2">Название</th><th className="p-2">Plan</th></tr></thead>
            <tbody>
              {rows.map((r,idx)=>(<tr key={idx} className="border-t"><td className="p-1">{r.city_code}</td><td className="p-1">{r.store_id}</td><td className="p-1">{r.store_name}</td><td className="p-1">{r.plan_qty}</td></tr>))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Задать/изменить план</div>
        <div className="grid md:grid-cols-3 gap-2">
          <input className="border rounded px-2 py-1" placeholder="Store ID" value={storeId} onChange={e=>setStoreId(e.target.value)} />
          <input type="number" className="border rounded px-2 py-1" placeholder="Plan qty" value={planQty} onChange={e=>setPlanQty(Number(e.target.value||0))} />
          <button className="px-3 py-2 rounded bg-green-600 text-white" onClick={save}>Сохранить</button>
        </div>
      </div>
    </div>
  );
}
