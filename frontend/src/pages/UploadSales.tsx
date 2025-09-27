import { useState } from "react";
import { api } from "../shared/api/http";

type UploadResult = { inserted: number; updated: number; errors: string[] };

export default function UploadSales() {
  const [promotersRes, setPromotersRes] = useState<UploadResult | null>(null);
  const [networksRes, setNetworksRes] = useState<UploadResult | null>(null);
  const [loading, setLoading] = useState(false);

  const onUpload = async (type: "promoters" | "networks", file?: File | null) => {
    if (!file) return;
    setLoading(true);
    try {
      const { data } = type === "promoters"
        ? await api.uploadPromoters(file)
        : await api.uploadNetworks(file);
      (type === "promoters" ? setPromotersRes : setNetworksRes)(data);
    } catch (e) {
      (type === "promoters" ? setPromotersRes : setNetworksRes)({
        inserted: 0, updated: 0, errors: [(e as any)?.message || "Ошибка"],
      });
    } finally { setLoading(false); }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Загрузка продаж</h2>

      <section style={{ marginTop: 16 }}>
        <h3>Промоутеры (CSV/XLSX)</h3>
        <input type="file" accept=".csv,.xlsx,.xls"
               onChange={(e) => onUpload("promoters", e.target.files?.[0])} />
        {promotersRes && (
          <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 12, marginTop: 8 }}>
            {JSON.stringify(promotersRes, null, 2)}
          </pre>
        )}
      </section>

      <section style={{ marginTop: 24 }}>
        <h3>Сети (CSV/XLSX)</h3>
        <input type="file" accept=".csv,.xlsx,.xls"
               onChange={(e) => onUpload("networks", e.target.files?.[0])} />
        {networksRes && (
          <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 12, marginTop: 8 }}>
            {JSON.stringify(networksRes, null, 2)}
          </pre>
        )}
      </section>

      {loading && <p>Загружаю...</p>}

      <details style={{ marginTop: 24 }}>
        <summary>Форматы колонок (минимум)</summary>
        <pre style={{ whiteSpace: "pre-wrap" }}>
{`promoters:
store_name,sku_code,qty,sold_at,amount,promoter
Sulpak 1,OPPO-A38,2,2025-08-10,179980,Айгерим

networks:
store_name,sku_code,qty,sold_at,amount,source_doc
Sulpak 1,OPPO-A38,3,2025-08-10,269970,RR-123`}
        </pre>
      </details>
    </div>
  );
}
