import React, { useEffect, useState } from 'react';
import { listNetworks, fetchBonusGrid, saveBonusGrid } from '../shared/api/bonus';
import { exportBonusCSV, importBonusCSV } from '../shared/api/bonus_csv';

function firstDayOfMonthISO(d = new Date()){
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0,10);
}

export default function OfficeBonusGrid(){
  const [nets, setNets] = useState<string[]>([]);
  const [net, setNet] = useState<string>('');
  const [month, setMonth] = useState<string>(firstDayOfMonthISO());
  const [rows, setRows] = useState<any[]>([]);
  const [saving, setSaving] = useState(false);
  const [file, setFile] = useState<File|null>(null);

  useEffect(()=>{
    listNetworks().then(d=>{ setNets(d.networks||[]); if (d.networks?.length) setNet(d.networks[0]); });
  }, []);

  useEffect(()=>{
    if (!net) return;
    fetchBonusGrid(net, month).then(d=> setRows(d.items||[]));
  }, [net, month]);

  const changeAmount = (i: number, v: string) => {
    const n = [...rows];
    n[i] = { ...n[i], amount: Number(v||0) };
    setRows(n);
  };

  const save = async () => {
    setSaving(true);
    try{
      await saveBonusGrid(net, rows.map(r=>({ sku_id: r.sku_id, amount: Number(r.amount||0) })), month);
      await fetchBonusGrid(net, month).then(d=> setRows(d.items||[]));
    } finally{
      setSaving(false);
    }
  };

  const doExport = async () => {
    const blob = await exportBonusCSV(net, month);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href=url; a.download=`bonus_${net}.csv`; a.click(); URL.revokeObjectURL(url);
  };

  const doImport = async () => {
    if (!file) return;
    await importBonusCSV(file, net, month);
    await fetchBonusGrid(net, month).then(d=> setRows(d.items||[]));
    setFile(null);
  };

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">Бонусные сетки по моделям (версионирование по месяцу)</h2>
      <div className="flex gap-3 items-end flex-wrap">
        <div>
          <div className="text-xs opacity-60">Сеть</div>
          <select className="border rounded px-2 py-1" value={net} onChange={e=>setNet(e.target.value)}>
            {nets.map(n=><option key={n} value={n}>{n}</option>)}
          </select>
        </div>
        <div>
          <div className="text-xs opacity-60">Месяц действия</div>
          <input type="date" className="border rounded px-2 py-1" value={month} onChange={e=>setMonth(e.target.value)} />
        </div>
        <button className="px-3 py-2 rounded bg-gray-800 text-white" onClick={save} disabled={saving || !rows.length}>
          {saving ? 'Сохранение…' : 'Сохранить'}
        </button>
        <button className="px-3 py-2 rounded bg-blue-700 text-white" onClick={doExport}>Экспорт CSV</button>
        <label className="px-3 py-2 rounded border cursor-pointer">
          Импорт CSV
          <input type="file" accept=".csv" className="hidden" onChange={e=>setFile(e.target.files?.[0]||null)} />
        </label>
        <button className="px-3 py-2 rounded bg-green-700 text-white" onClick={doImport} disabled={!file}>Загрузить</button>
      </div>

      <div className="p-3 border rounded overflow-auto">
        <table className="min-w-[700px] text-sm">
          <thead><tr className="bg-gray-50"><th className="p-2">SKU</th><th className="p-2">Модель</th><th className="p-2">Бонус/шт</th></tr></thead>
          <tbody>
            {rows.map((r,idx)=>(
              <tr key={r.sku_id} className="border-t">
                <td className="p-1">{r.sku_id}</td>
                <td className="p-1">{r.model}</td>
                <td className="p-1">
                  <input type="number" className="border rounded px-2 py-1 w-[140px]" value={r.amount ?? 0}
                         onChange={e=>changeAmount(idx, e.target.value)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="text-xs opacity-60">
        Сохранение/импорт создаёт новую версию на выбранный месяц. Экспорт формирует CSV по текущей версии.
      </div>
    </div>
  );
}
