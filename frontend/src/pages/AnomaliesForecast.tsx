import { useState } from "react";
import { api } from "../shared/api/http";

export default function AnomaliesForecast() {
  const [store, setStore] = useState("A01");
  const [sku, setSku] = useState("OPPO-A1K");
  const [anoms, setAnoms] = useState<any[]>([]);
  const [fc, setFc] = useState<any[]>([]);
  const loadAnoms = async () => {
    const { data } = await api.anomalies.list({ store, sku });
    setAnoms(data);
  };
  const loadFc = async () => {
    const { data } = await api.forecast.sku(sku, store, 14);
    setFc(data);
  };
  return (
    <div style={{ padding: 16 }}>
      <h2>Аномалии / Прогноз</h2>
      <div style={{ display:"flex", gap:8, alignItems:"center" }}>
        <input placeholder="Store" value={store} onChange={(e)=>setStore(e.target.value)} />
        <input placeholder="SKU" value={sku} onChange={(e)=>setSku(e.target.value)} />
        <button onClick={loadAnoms}>Обновить аномалии</button>
        <button onClick={loadFc}>Обновить прогноз</button>
      </div>
      <h3 style={{ marginTop: 12 }}>Аномалии</h3>
      <table style={{ width:"100%", maxWidth:900, borderCollapse:"collapse" }}>
        <thead><tr><th>ID</th><th>Type</th><th>SKU</th><th>Store</th><th>Date</th><th>Score</th></tr></thead>
        <tbody>
          {anoms.map((a:any)=>(<tr key={a.id}><td>{a.id}</td><td>{a.type}</td><td>{a.sku}</td><td>{a.store}</td><td>{a.date}</td><td>{a.score}</td></tr>))}
        </tbody>
      </table>
      <h3 style={{ marginTop: 12 }}>Прогноз (14 дней)</h3>
      <table style={{ width:"100%", maxWidth:900, borderCollapse:"collapse" }}>
        <thead><tr><th>Date</th><th>SKU</th><th>Store</th><th>Forecast</th></tr></thead>
        <tbody>
          {fc.map((r:any, i:number)=>(<tr key={i}><td>{r.date}</td><td>{r.sku}</td><td>{r.store||""}</td><td>{r.forecast}</td></tr>))}
        </tbody>
      </table>
    </div>
  );
}
