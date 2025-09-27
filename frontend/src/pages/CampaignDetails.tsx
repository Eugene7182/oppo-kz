import { useState } from "react";
import { api } from "../shared/api/http";

export default function CampaignDetails() {
  const [id, setId] = useState<number>(1);
  const [data, setData] = useState<any>(null);
  const load = async () => {
    const { data } = await api.campaigns.getById(id);
    setData(data);
  };
  return (
    <div style={{ padding: 16 }}>
      <h2>Кампания — детали</h2>
      <div style={{ display:"flex", gap:8, alignItems:"center" }}>
        <input type="number" value={id} onChange={(e)=>setId(parseInt(e.target.value||"0"))} style={{ width:120 }} />
        <button onClick={load}>Загрузить</button>
      </div>
      {data && (
        <div style={{ marginTop:12 }}>
          <div><b>{data.name}</b> ({data.start} → {data.end})</div>
          <div>Stores: {(data.stores||[]).join(", ")}</div>
          <div>SKUs: {(data.skus||[]).join(", ")}</div>
          <div>Mechanics:</div>
          <pre>{JSON.stringify(data.mechanics||{}, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
