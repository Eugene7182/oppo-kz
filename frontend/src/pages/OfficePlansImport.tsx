import React, { useState } from 'react';
import { importPlansCSV } from '../shared/api/plans_import';

function firstDayOfMonthISO(d=new Date()){ return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0,10); }

export default function OfficePlansImport(){
  const [file, setFile] = useState<File|null>(null);
  const [month, setMonth] = useState<string>(firstDayOfMonthISO());
  const [msg, setMsg] = useState<string>('');

  const submit = async () => {
    if (!file){ setMsg('Выберите CSV'); return; }
    try{
      const r = await importPlansCSV(file, month);
      setMsg(`Импортировано: ${r.imported}`);
    }catch(e){ setMsg('Ошибка импорта'); }
  };

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">Импорт планов (CSV)</h2>
      <div className="text-sm opacity-70">Ожидаемые колонки: <b>store_id, plan_qty</b>. Месяц применяется ко всем строкам.</div>
      <div className="grid md:grid-cols-3 gap-2">
        <div><div className="text-xs opacity-60">Месяц</div><input type="date" className="border rounded px-2 py-1 w-full" value={month} onChange={e=>setMonth(e.target.value)} /></div>
        <div><div className="text-xs opacity-60">CSV</div><input type="file" accept=".csv" onChange={e=>setFile(e.target.files?.[0]||null)} /></div>
        <div className="flex items-end"><button className="px-3 py-2 rounded bg-green-600 text-white" onClick={submit}>Импортировать</button></div>
      </div>
      {msg && <div className="text-sm">{msg}</div>}
    </div>
  );
}
