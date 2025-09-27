import React, { useEffect, useState } from 'react';
import { fetchABCXYZ, fetchForecast } from '../shared/api/ai_advanced';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function OfficeABCXYZ(){
  const [days, setDays] = useState(60);
  const [items, setItems] = useState<any[]>([]);
  const [series, setSeries] = useState<any[]>([]);
  const [forecast, setForecast] = useState<any[]>([]);

  const load = async () => {
    const ab = await fetchABCXYZ({ days });
    setItems(ab.items || []);
    const fc = await fetchForecast({ group_by: 'total', horizon_days: 30 });
    setSeries(fc.series || []);
    setForecast(fc.forecast || []);
  };
  useEffect(()=>{ load(); }, []);

  const data = [...series, ...forecast.map(f=>({ ...f, forecast: true }))]
    .map(x=>({ ...x, qty: Number(x.qty || 0) }));

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-semibold">ABC/XYZ и прогноз</h2>

      <div className="flex items-end gap-2">
        <div>
          <div className="text-xs opacity-60">Дней для ABC/XYZ</div>
          <input type="number" className="border rounded px-2 py-1 w-[120px]" value={days} onChange={e=>setDays(Number(e.target.value||60))}/>
        </div>
        <button className="px-3 py-2 rounded bg-gray-800 text-white" onClick={load}>Обновить</button>
      </div>

      <div className="p-3 border rounded overflow-auto">
        <table className="min-w-[700px] text-sm">
          <thead><tr className="bg-gray-50"><th className="p-2">SKU</th><th className="p-2">Total</th><th className="p-2">ABC</th><th className="p-2">XYZ</th></tr></thead>
          <tbody>
            {items.map((r,idx)=>(
              <tr key={idx} className="border-t">
                <td className="p-1">{r.sku_id}</td>
                <td className="p-1">{Math.round(r.total_qty)}</td>
                <td className="p-1">{r.ABC}</td>
                <td className="p-1">{r.XYZ}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Прогноз продаж (суммарный)</div>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="qty" />
          </LineChart>
        </ResponsiveContainer>
        <div className="text-xs opacity-60 mt-2">Скользящее среднее (EWMA) и плоский прогноз на 30 дней вперёд.</div>
      </div>
    </div>
  );
}
