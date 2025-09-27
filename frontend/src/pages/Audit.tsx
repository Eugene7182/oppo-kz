import { useEffect, useState } from "react";
import { api } from "../shared/api/http";

type Log = { id: number; actor_username?: string; action: string; entity?: string; entity_id?: string; ts: string };

export default function Audit() {
  const [rows, setRows] = useState<Log[]>([]);
  useEffect(()=>{ api.audit.list().then(({data})=> setRows(data)); },[]);
  return (
    <div style={{ padding: 16 }}>
      <h2>Аудит-лог</h2>
      <table style={{ width:"100%", borderCollapse:"collapse"}}>
        <thead><tr><th>ID</th><th>Time</th><th>Actor</th><th>Action</th><th>Entity</th><th>Entity ID</th></tr></thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{new Date(r.ts).toLocaleString()}</td>
              <td>{r.actor_username||""}</td>
              <td>{r.action}</td>
              <td>{r.entity||""}</td>
              <td>{r.entity_id||""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
