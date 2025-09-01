import React, { useEffect, useState } from 'react';
import { postSale, postZeroDay, SalePayload } from '../shared/api/sales';
import { listMemoryOptions } from '../shared/api/sku_memory';
import { api } from '../shared/api/http';

function useSalesQueue(){
  const FAIL_KEY='sales_queue_failcount_v1';

  const KEY = 'sales_queue_v1';
  const load = () => {
    try{ return JSON.parse(localStorage.getItem(KEY)||'[]'); }catch{ return []; }
  };
  const save = (arr:any[]) => localStorage.setItem(KEY, JSON.stringify(arr));
  const push = (item:any) => { const a = load(); a.push(item); save(a); };
  const popAll = () => { const a = load(); save([]); return a; };
  const len = () => load().length; return { load, push, popAll, toCSV, incFail, resetFail, len };
}

export default function PromoterSalesEntry(){
  const [skus, setSkus] = useState<{ sku_id:string; model:string }[]>([]);
  const [dateISO, setDateISO] = useState<string>(new Date().toISOString().slice(0,10));
  const [store, setStore] = useState('');
  const [sku, setSku] = useState('');
  const [modelName, setModelName] = useState('');
  const [mem, setMem] = useState<number>(128);
  const [memOpts, setMemOpts] = useState<number[]>([]);
  const [queueLen, setQueueLen] = useState<number>(0);
  const [lastOk, setLastOk] = useState<string>(localStorage.getItem('sales_last_ok_ts')||'—');
  const [qty, setQty] = useState<number>(1);
  const [price, setPrice] = useState<number>(0);
  const [network, setNetwork] = useState('');
  const [msg, setMsg] = useState<string>('');
  const [showManual, setShowManual] = useState<boolean>(false);
  const queue = useSalesQueue();

  useEffect(()=>{
    api.get('/api/v1/skus').then(r=> setSkus(r.data.items||[])).catch(()=>{});
  }, []);

  useEffect(()=>{
    const timer = setInterval(async ()=>{ setQueueLen(queue.len());
      // try to flush queue
      const items = queue.popAll();
      for (const it of items){
        try{ await postSale(it); queue.resetFail(); localStorage.setItem('sales_last_ok_ts', new Date().toISOString()); setLastOk(new Date().toISOString()); }
        catch{ const f=queue.incFail(); queue.push(it); break; }
      }
    }, 5000);
    return ()=>clearInterval(timer);
  }, []);

  const submit = async () => {
    const payload: SalePayload = { date: dateISO, store_id: store, sku_id: sku, model: modelName, memory_gb: mem, qty, price_per_unit: price, network_id: network };
    if (!store || !sku || qty<=0){ setMsg('Заполните магазин, модель и количество'); return; }
    try{
      await postSale(payload);
      setMsg('Продажа записана');
    }catch(e){
      queue.push(payload);
      setMsg('Нет сети — записали в очередь. Синхронизируем при появлении сети.'); setShowManual(true);
    }
  };

  const zero = async () => {
    try{ await postZeroDay(dateISO); setMsg('Нулевой день отмечен'); }
    catch{ setMsg('Ошибка отметки нулевого дня'); }
  };

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">Ввод продаж (офлайн-очередь поддерживается)</h2>
      <div className="text-xs opacity-70">Очередь: {queueLen} | Последняя удачная отправка: {lastOk}</div>

      <div className="grid md:grid-cols-3 gap-2">
        <div><div className="text-xs opacity-60">Дата</div><input type="date" className="border rounded px-2 py-1 w-full" value={dateISO} onChange={e=>setDateISO(e.target.value)} /></div>
        <div><div className="text-xs opacity-60">Магазин (Store ID)</div><input className="border rounded px-2 py-1 w-full" value={store} onChange={e=>setStore(e.target.value)} /></div>
        <div><div className="text-xs opacity-60">Сеть</div><input className="border rounded px-2 py-1 w-full" value={network} onChange={e=>setNetwork(e.target.value)} /></div>
      </div>

      <div className="grid md:grid-cols-3 gap-2">
        <div>
          <div className="text-xs opacity-60">Модель</div>
          <select className="border rounded px-2 py-1 w-full" value={sku} onChange={e=>{ setSku(e.target.value); const mm = skus.find(s=>s.sku_id===e.target.value); setModelName(mm?.model||''); listMemoryOptions(e.target.value).then(d=>setMemOpts(d.items||[])).catch(()=>setMemOpts([])); }}>
            <option value="">— выберите —</option>
            {skus.map(s=>(<option key={s.sku_id} value={s.sku_id}>{s.model}</option>))}
          </select>
        </div>
        <div><div className="text-xs opacity-60">Память (GB)</div>
          {memOpts.length>0 ? (
            <select className="border rounded px-2 py-1 w-full" value={mem} onChange={e=>setMem(Number(e.target.value||0))}>
              {memOpts.map(m=>(<option key={m} value={m}>{m}</option>))}
            </select>
          ) : (
            <input type="number" className="border rounded px-2 py-1 w-full" value={mem} onChange={e=>setMem(Number(e.target.value||0))} />
          )}
        </div>
        <div><div className="text-xs opacity-60">Кол-во</div><input type="number" className="border rounded px-2 py-1 w-full" value={qty} onChange={e=>setQty(Number(e.target.value||0))} /></div>
      </div>

      <div className="grid md:grid-cols-3 gap-2">
        <div><div className="text-xs opacity-60">Цена за шт (необязательно)</div><input type="number" className="border rounded px-2 py-1 w-full" value={price} onChange={e=>setPrice(Number(e.target.value||0))} /></div>
      </div>

      <div className="flex gap-2">
        <button className="px-3 py-2 rounded bg-green-600 text-white" onClick={submit}>Сохранить продажу</button>
        <button className="px-3 py-2 rounded bg-gray-700 text-white" onClick={zero}>Сегодня ноль (необязательно)</button>
      </div>
      {msg && <div className="text-sm">{msg}</div>}
      {showManual && (

      <div className="p-3 border rounded bg-red-50">
        <div className="font-medium">Похоже, сеть нестабильна. Можно передать данные вручную.</div>
        <div className="flex gap-2 mt-2">
          <button className="px-3 py-2 rounded bg-red-600 text-white" onClick={()=>{
            const csv = queue.toCSV(queue.load());
            const blob = new Blob([csv], {type:'text/csv'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href=url; a.download='sales_offline_queue.csv'; a.click(); URL.revokeObjectURL(url);
          }}>Экспорт в CSV</button>
          <button className="px-3 py-2 rounded bg-gray-700 text-white" onClick={()=>setShowManual(false)}>Понятно</button>
        </div>
        <div className="text-xs opacity-60 mt-1">Отправьте файл супервайзеру/офису для ручной загрузки.</div>
      </div>

      )}

      <div className="text-xs opacity-60">
        Если нет интернета — продажи попадут в локальную очередь и отправятся автоматически в течение ~5 секунд после восстановления сети.
      </div>
    </div>
  );
}
