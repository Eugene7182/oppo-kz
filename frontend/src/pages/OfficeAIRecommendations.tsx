import React, { useEffect, useState } from 'react';
import { fetchReplenish, fetchTransfer, fetchAnomalies } from '../shared/api/ai';

export default function OfficeAIRecommendations(){
  const [days, setDays] = useState(28);
  const [lead, setLead] = useState(3);
  const [target, setTarget] = useState(7);
  const [minq, setMinq] = useState(1);
  const [sameCity, setSameCity] = useState(true);
  const [sameNet, setSameNet] = useState(true);

  const [repl, setRepl] = useState<any[]>([]);
  const [pairs, setPairs] = useState<any[]>([]);
  const [anom, setAnom] = useState<any[]>([]);

  const load = async () => {
    const [r, t, a] = await Promise.all([
      fetchReplenish({ days, leadtime: lead, target_days: target, min_qty: minq, same_city_only: sameCity, same_network_only: sameNet }),
      fetchTransfer({ days, leadtime: lead, target_days: target, min_qty: minq, same_city_only: sameCity, same_network_only: sameNet }),
      fetchAnomalies()
    ]);
    setRepl(r.items || []);
    setPairs(t.pairs || []);
    setAnom(a.items || []);
  };

  useEffect(()=>{ load(); }, []);

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-semibold">AI Рекомендации</h2>

      <div className="grid md:grid-cols-6 gap-2 items-end">
        <div><div className="text-xs opacity-60">Дней в расчёте</div><input type="number" className="border rounded px-2 py-1 w-full" value={days} onChange={e=>setDays(Number(e.target.value||28))}/></div>
        <div><div className="text-xs opacity-60">Лид-тайм, дн</div><input type="number" className="border rounded px-2 py-1 w-full" value={lead} onChange={e=>setLead(Number(e.target.value||3))}/></div>
        <div><div className="text-xs opacity-60">Целевой запас, дн</div><input type="number" className="border rounded px-2 py-1 w-full" value={target} onChange={e=>setTarget(Number(e.target.value||7))}/></div>
        <div><div className="text-xs opacity-60">Мин. рекомендация</div><input type="number" className="border rounded px-2 py-1 w-full" value={minq} onChange={e=>setMinq(Number(e.target.value||1))}/></div>
        <label className="inline-flex items-center gap-2"><input type="checkbox" checked={sameCity} onChange={e=>setSameCity(e.target.checked)}/> в одном городе</label>
        <label className="inline-flex items-center gap-2"><input type="checkbox" checked={sameNet} onChange={e=>setSameNet(e.target.checked)}/> в одной сети</label>
        <div className="md:col-span-6"><button className="px-3 py-2 rounded bg-gray-800 text-white" onClick={load}>Обновить рекомендации</button></div>
      </div>

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Пополнение</div>
        <div className="overflow-auto">
          <table className="min-w-[900px] text-sm">
            <thead><tr className="bg-gray-50"><th className="p-2">City</th><th className="p-2">Network</th><th className="p-2">Store</th><th className="p-2">SKU</th><th className="p-2">Avg/day</th><th className="p-2">On hand</th><th className="p-2">Target</th><th className="p-2">Rec qty</th></tr></thead>
            <tbody>
              {repl.map((r,idx)=>(
                <tr key={idx} className="border-t">
                  <td className="p-1">{r.city_code || ''}</td>
                  <td className="p-1">{r.network_id || ''}</td>
                  <td className="p-1">{r.store_id}</td>
                  <td className="p-1">{r.sku_id}</td>
                  <td className="p-1">{(r.avg_daily||0).toFixed(2)}</td>
                  <td className="p-1">{r.on_hand||0}</td>
                  <td className="p-1">{Math.round(r.target_units||0)}</td>
                  <td className="p-1 font-semibold">{r.rec_qty}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Перемещения (внутри города/сети)</div>
        <div className="overflow-auto">
          <table className="min-w-[800px] text-sm">
            <thead><tr className="bg-gray-50"><th className="p-2">City</th><th className="p-2">Network</th><th className="p-2">SKU</th><th className="p-2">From</th><th className="p-2">To</th><th className="p-2">Qty</th></tr></thead>
            <tbody>
              {pairs.map((p,idx)=>(
                <tr key={idx} className="border-t">
                  <td className="p-1">{p.city_code || ''}</td>
                  <td className="p-1">{p.network_id || ''}</td>
                  <td className="p-1">{p.sku_id}</td>
                  <td className="p-1">{p.from_store}</td>
                  <td className="p-1">{p.to_store}</td>
                  <td className="p-1 font-semibold">{p.qty}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Аномалии (7д vs 7д)</div>
        <div className="overflow-auto">
          <table className="min-w-[800px] text-sm">
            <thead><tr className="bg-gray-50"><th className="p-2">Store</th><th className="p-2">SKU</th><th className="p-2">7д</th><th className="p-2">Пред.7д</th><th className="p-2">Тип</th><th className="p-2">Δ</th></tr></thead>
            <tbody>
              {anom.map((a,idx)=>(
                <tr key={idx} className="border-t">
                  <td className="p-1">{a.store_id}</td>
                  <td className="p-1">{a.sku_id}</td>
                  <td className="p-1">{Math.round(a.qty_7)}</td>
                  <td className="p-1">{Math.round(a.qty_prev7)}</td>
                  <td className="p-1">{a.kind}</td>
                  <td className="p-1">{(a.change*100).toFixed(0)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-3 border rounded">
        <div className="font-medium mb-2">Экспорт комплаенса (неделя)</div>
        <a className="px-3 py-2 inline-block rounded bg-gray-800 text-white" href="/api/v1/office/compliance/export.csv" target="_blank" rel="noreferrer">
          Скачать CSV
        </a>
      </div>
    </div>
  );
}
