import { useEffect, useState } from "react";
import { api } from "../shared/api/http";

type Row = { store_id:number; store_name:string; sku_code:string; qty:number; sold_at:string; amount:number };

export default function Promoter() {
  const today = new Date().toISOString().slice(0,10);
  const [me, setMe] = useState<any>(null);
  const [stores, setStores] = useState<number[]>([]);
  const [currentStore, setCurrentStore] = useState<number| "">("");
  const [lines, setLines] = useState<Row[]>([]);
  const [sku, setSku] = useState("");  // маркетинговый код, напр. OPPO-A38
  const [qty, setQty] = useState<number>(1);
  const [amount, setAmount] = useState<number>(0);
  const [date, setDate] = useState(today);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api.me().then(({data}) => setMe(data)).catch(()=>{});
    api.myStores().then(({data}) => setStores(data)).catch(()=>{});
  }, []);

  const add = () => {
    if (!currentStore || !sku.trim() || !qty) return;
    const store_name = `store_${currentStore}`; // дружелюбное имя по id; можно улучшить (подтянуть список магазинов)
    setLines(prev => [...prev, { store_id:Number(currentStore), store_name, sku_code: sku.trim().toUpperCase(), qty, sold_at: date, amount }]);
    setSku(""); setQty(1); setAmount(0);
  };

  const upload = async () => {
    if (!lines.length) return;
    // Соберём CSV с колонками как в нашем загрузчике промоутеров:
    // store_name, sku_code, qty, sold_at, amount, promoter
    const promoter = me?.name || "promoter";
    const header = "store_name,sku_code,qty,sold_at,amount,promoter\n";
    const body = lines.map(r => [r.store_name, r.sku_code, r.qty, r.sold_at, r.amount, promoter].join(",")).join("\n");
    const blob = new Blob([header + body], { type: "text/csv;charset=utf-8" });
    const file = new File([blob], `promoter_${Date.now()}.csv`, { type: "text/csv" });
    try {
      const { data } = await api.uploadPromoters(file);
      setMsg(`Загружено: inserted=${data.inserted}, updated=${data.updated}, errors=${data.errors?.length||0}`);
      setLines([]);
    } catch (e:any) {
      setMsg(e?.response?.data?.detail || "Ошибка загрузки");
    }
  };

  return (
    <div style={{ padding:24 }}>
      <h2>Панель промоутера</h2>
      {!me && <p>Не авторизован (войдите на /login)</p>}
      {me && <p>Вы вошли как: {me.name} ({me.role})</p>}

      <div style={{ display:"flex", gap:8, alignItems:"center", flexWrap:"wrap" }}>
        <label>Магазин ID:</label>
        <input type="number" value={currentStore} onChange={e=>setCurrentStore(e.target.value?Number(e.target.value):"")} style={{ width:100 }}/>
        {/* При желании подгрузим реальные имена магазинов по id и сделаем выпадающий список */}
      </div>

      <div style={{ marginTop:12, display:"flex", gap:8, alignItems:"center", flexWrap:"wrap" }}>
        <input placeholder="SKU (напр. OPPO-A38)" value={sku} onChange={e=>setSku(e.target.value)} style={{ width:180 }}/>
        <input type="number" placeholder="Qty" value={qty} onChange={e=>setQty(Number(e.target.value||0))} style={{ width:90 }}/>
        <input type="number" placeholder="Amount" value={amount} onChange={e=>setAmount(Number(e.target.value||0))} style={{ width:120 }}/>
        <input type="date" value={date} onChange={e=>setDate(e.target.value)} />
        <button onClick={add}>Добавить строку</button>
      </div>

      <ul style={{ marginTop:10 }}>
        {lines.map((r,i) => <li key={i}>{r.store_id} · {r.sku_code} · {r.qty} шт · {r.amount} · {r.sold_at}</li>)}
      </ul>

      <div style={{ marginTop:12 }}>
        <button onClick={upload} disabled={!lines.length}>Отправить</button>
      </div>

      {msg && <p style={{ marginTop:10 }}>{msg}</p>}
    </div>
  );
}
