import { useState } from "react";
import { api } from "../shared/api/http";

type ReconRow = {
  store_id: number; sku_id: number; date: string;
  qty_network: number; qty_promoters: number; delta: number;
};

export default function Reconciliation() {
  const today = new Date().toISOString().slice(0, 10);
  const [dateFrom, setDateFrom] = useState(today);
  const [dateTo, setDateTo] = useState(today);
  const [storeId, setStoreId] = useState<number | "">("");
  const [rows, setRows] = useState<ReconRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  const load = async () => {
    setLoading(true); setMsg("");
    try {
      const { data } = await api.reconSummary({
        date_from: dateFrom, date_to: dateTo,
        store_id: typeof storeId === "number" ? storeId : undefined,
      });
      setRows(data);
    } catch (e: any) {
      setMsg(e?.message || "Ошибка загрузки сверки");
    } finally { setLoading(false); }
  };

  const approve = async (row: ReconRow, source: "network" | "promoter") => {
    setMsg("");
    try {
      const { data } = await api.reconApprove({
        store_id: row.store_id, sku_id: row.sku_id, date: row.date, source,
      });
      setMsg(`Approved: ${JSON.stringify(data)}`);
    } catch (e: any) {
      setMsg(e?.message || "Ошибка апрува");
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Сверка и апрув</h2>

      <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12 }}>
        <label>С:</label><input type="date" value={dateFrom} onChange={e=>setDateFrom(e.target.value)} />
        <label>По:</label><input type="date" value={dateTo} onChange={e=>setDateTo(e.target.value)} />
        <label>Store ID (опц.):</label>
        <input type="number" value={storeId} onChange={e=>setStoreId(e.target.value ? Number(e.target.value) : "")} style={{ width: 100 }} />
        <button onClick={load}>Загрузить</button>
      </div>

      {loading && <p>Загружаю...</p>}
      {msg && <p>{msg}</p>}

      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>Store</th>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>SKU</th>
            <th style={{ borderBottom: "1px solid #ccc", textAlign: "left" }}>Date</th>
            <th style={{ borderBottom: "1px solid #ccc" }}>Networks</th>
            <th style={{ borderBottom: "1px solid #ccc" }}>Promoters</th>
            <th style={{ borderBottom: "1px solid #ccc" }}>Δ</th>
            <th style={{ borderBottom: "1px solid #ccc" }}>Approve</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td>{r.store_id}</td>
              <td>{r.sku_id}</td>
              <td>{r.date}</td>
              <td style={{ textAlign: "center" }}>{r.qty_network}</td>
              <td style={{ textAlign: "center" }}>{r.qty_promoters}</td>
              <td style={{ textAlign: "center", color: r.delta > 0 ? "green" : r.delta < 0 ? "red" : "inherit" }}>
                {r.delta}
              </td>
              <td style={{ textAlign: "center" }}>
                <button onClick={() => approve(r, "network")} style={{ marginRight: 6 }}>Network</button>
                <button onClick={() => approve(r, "promoter")}>Promoter</button>
              </td>
            </tr>
          ))}
          {!rows.length && !loading && (
            <tr><td colSpan={7} style={{ padding: 8, color: "#777" }}>Нет расхождений или не загружено</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
