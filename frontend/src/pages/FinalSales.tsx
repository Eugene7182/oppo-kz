import { useState } from "react";
import { api } from "../shared/api/http";

type FinalRow = { id:number; store_id:number; sku_id:number; date:string; qty:number; amount:number; source:string };

export default function FinalSales() {
  const today = new Date().toISOString().slice(0,10);
  const [dateFrom, setDateFrom] = useState(today);
  const [dateTo, setDateTo] = useState(today);
  const [storeId, setStoreId] = useState<number| "">("");
  const [skuId, setSkuId] = useState<number| "">("");
  const [rows, setRows] = useState<FinalRow[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    const { data } = await api.finalSales({
      date_from: dateFrom, date_to: dateTo,
      store_id: typeof storeId === "number" ? storeId : undefined,
      sku_id: typeof skuId === "number" ? skuId : undefined,
      limit: 1000,
    });
    setRows(data);
    setLoading(false);
  };

  const exportCsv = () => {
    const url = api.finalSalesExportCsvUrl({
      date_from: dateFrom, date_to: dateTo,
      store_id: typeof storeId === "number" ? storeId : undefined,
      sku_id: typeof skuId === "number" ? skuId : undefined,
    });
    // Откроем в новой вкладке — скачивание без CORS-сложностей
    window.open(url, "_blank");
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Итоговые продажи (sales_final)</h2>

      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", marginBottom: 12 }}>
        <label>С:</label><input type="date" value={dateFrom} onChange={e=>setDateFrom(e.target.value)} />
        <label>По:</label><input type="date" value={dateTo} onChange={e=>setDateTo(e.target.value)} />
        <label>StoreID:</label><input type="number" value={storeId} onChange={e=>setStoreId(e.target.value?Number(e.target.value):"")} style={{ width: 90 }} />
        <label>SKUID:</label><input type="number" value={skuId} onChange={e=>setSkuId(e.target.value?Number(e.target.value):"")} style={{ width: 90 }} />
        <button onClick={load}>Загрузить</button>
        <button onClick={exportCsv}>Экспорт CSV</button>
      </div>

      {loading && <p>Загрузка...</p>}

      <table style={{ borderCollapse:"collapse", width:"100%" }}>
        <thead>
          <tr>
            <th style={{ borderBottom:"1px solid #ccc", textAlign:"left" }}>Store</th>
            <th style={{ borderBottom:"1px solid #ccc", textAlign:"left" }}>SKU</th>
            <th style={{ borderBottom:"1px solid #ccc", textAlign:"left" }}>Date</th>
            <th style={{ borderBottom:"1px solid #ccc" }}>Qty</th>
            <th style={{ borderBottom:"1px solid #ccc" }}>Amount</th>
            <th style={{ borderBottom:"1px solid #ccc" }}>Source</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id}>
              <td>{r.store_id}</td>
              <td>{r.sku_id}</td>
              <td>{r.date}</td>
              <td style={{ textAlign:"center" }}>{r.qty}</td>
              <td style={{ textAlign:"center" }}>{r.amount}</td>
              <td style={{ textAlign:"center" }}>{r.source}</td>
            </tr>
          ))}
          {!rows.length && !loading && <tr><td colSpan={6} style={{ color:"#777" }}>Нет данных</td></tr>}
        </tbody>
      </table>
    </div>
  );
}
