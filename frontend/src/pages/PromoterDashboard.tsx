import React, { useEffect, useState } from 'react';
import { api } from '../shared/api/http';

function Progress({ value }: { value: number }){
  const v = Math.max(0, Math.min(100, Math.round(value||0)));
  return (
    <div className="w-full border rounded h-6 overflow-hidden">
      <div className="h-6 bg-green-600 text-white text-xs flex items-center justify-center" style={{ width: v + '%' }}>{v}%</div>
    </div>
  );
}

export default function PromoterDashboard(){
  const [data, setData] = useState<any>(null);
  const load = async () => {
    const r = await api.get('/api/v1/promoter/me/dashboard');
    setData(r.data);
  };
  useEffect(()=>{ load(); }, []);

  if (!data) return <div className="p-4">Загрузка…</div>;

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-semibold">Мой план и бонусы</h2>
      <div className="grid md:grid-cols-3 gap-3">
        <div className="p-3 border rounded">План на месяц: <b>{Math.round(data.plan_qty||0)}</b></div>
        <div className="p-3 border rounded">MTD: <b>{Math.round(data.mtd_qty||0)}</b></div>
        <div className="p-3 border rounded">Прогноз (EOM): <b>{Math.round(data.eom_qty||0)}</b></div>
      </div>
      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Прогресс к плану</div>
        <Progress value={data.progress_pct||0} />
      </div>
      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Оценка бонуса (по сетям)</div>
        <div className="overflow-auto">
          <table className="min-w-[700px] text-sm">
            <thead><tr className="bg-gray-50"><th className="p-2">Store</th><th className="p-2">Network</th><th className="p-2">Qty MTD</th><th className="p-2">Bonus / unit</th><th className="p-2">Бонус</th></tr></thead>
            <tbody>
              {(data.bonus?.details||[]).map((d:any, idx:number)=>(
                <tr key={idx} className="border-t">
                  <td className="p-1">{d.store_id}</td>
                  <td className="p-1">{d.network_id}</td>
                  <td className="p-1">{Math.round(d.qty||0)}</td>
                  <td className="p-1">{Number(d.per_unit||0).toFixed(2)}</td>
                  <td className="p-1">{Number(d.bonus||0).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-2">Итого бонус (оценка): <b>{Number(data.bonus?.total_bonus||0).toFixed(2)}</b></div>
      </div>
    </div>
  );
}
