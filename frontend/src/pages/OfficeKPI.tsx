import React, { useEffect, useState } from 'react';
import { kpiOffice } from '../shared/api/kpi';

function Card({title, value}:{title:string; value:any}){
  return <div className="p-3 border rounded"><div className="text-xs opacity-60">{title}</div><div className="text-xl font-semibold">{value}</div></div>;
}

export default function OfficeKPI(){
  const [data, setData] = useState<any>(null);
  useEffect(()=>{ kpiOffice().then(setData); }, []);

  if (!data) return <div className="p-4">Загрузка…</div>;
  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">KPI по всем городам ({data.month})</h2>
      <div className="grid md:grid-cols-3 gap-3">
        <Card title="План" value={Math.round(data.plan)} />
        <Card title="Факт (MTD)" value={Math.round(data.fact)} />
        <Card title="Прогресс" value={`${Math.round(data.progress)}%`} />
      </div>
      <div className="p-3 border rounded overflow-auto">
        <table className="min-w-[800px] text-sm">
          <thead><tr className="bg-gray-50"><th className="p-2">Город</th><th className="p-2">План</th><th className="p-2">Факт</th><th className="p-2">%</th></tr></thead>
          <tbody>
            {(data.cities||[]).map((r:any, idx:number)=>(
              <tr key={idx} className="border-t">
                <td className="p-1">{r.city_code}</td>
                <td className="p-1">{r.plan_qty}</td>
                <td className="p-1">{r.fact_qty}</td>
                <td className="p-1">{Math.round(r.progress)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
