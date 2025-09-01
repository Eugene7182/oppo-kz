import { useState } from "react";
import { api } from "../shared/api/http";

type Item = { sku: string; from_store: string; to_store: string; qty: number };

export default function TransfersApply() {
  const [items, setItems] = useState<Item[]>([ { sku:"OPPO-A1K", from_store:"WH1", to_store:"A01", qty:10 } ]);
  const [result, setResult] = useState<any>(null);
  const add = () => setItems(a=>[...a, { sku:"OPPO-A1K", from_store:"WH1", to_store:"A01", qty:1 }]);
  const apply = async () => {
    const { data } = await api.transfers.apply(items);
    setResult(data);
  };
  return (
    <div style={{ padding: 16 }}>
      <h2>Перемещения — Применение</h2>
      <table style={{ width:"100%", maxWidth:900, borderCollapse:"collapse" }}>
        <thead><tr><th>SKU</th><th>From</th><th>To</th><th>QTY</th></tr></thead>
        <tbody>
          {items.map((r,i)=>(
            <tr key={i}>
              <td><input value={r.sku} onChange={(e)=>setItems(a=>a.map((x,j)=> j===i? {...x, sku:e.target.value}:x))} /></td>
              <td><input value={r.from_store} onChange={(e)=>setItems(a=>a.map((x,j)=> j===i? {...x, from_store:e.target.value}:x))} /></td>
              <td><input value={r.to_store} onChange={(e)=>setItems(a=>a.map((x,j)=> j===i? {...x, to_store:e.target.value}:x))} /></td>
              <td><input type="number" value={r.qty} onChange={(e)=>setItems(a=>a.map((x,j)=> j===i? {...x, qty:+e.target.value}:x))} style={{ width:100 }} /></td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginTop:8 }}>
        <button onClick={add}>+ Добавить строку</button>
        <button onClick={apply} style={{ marginLeft:8 }}>Применить</button>
      </div>
      {result && <pre style={{ marginTop:12 }}>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}
