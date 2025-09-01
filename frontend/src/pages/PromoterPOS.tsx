import { useEffect, useState } from "react";
import { api } from "../shared/api/http";

type Store = { id: number; name: string; city?: string; network?: string };
type SKU = { id: number; brand: string; model: string; code: string };

export default function PromoterPOS() {
  const [stores, setStores] = useState<Store[]>([]);
  const [skus, setSkus] = useState<SKU[]>([]);
  const [storeId, setStoreId] = useState<number | "">("");
  const [skuId, setSkuId] = useState<number | "">("");
  const [dateStr, setDateStr] = useState<string>(() => new Date().toISOString().slice(0, 10));
  const [qty, setQty] = useState<number | "">("");
  const [amount, setAmount] = useState<number | "">("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string>("");

  useEffect(() => {
    (async () => {
      try {
        const [st, sk] = await Promise.all([api.stores.list(), api.sku.list()]);
        setStores(st.data || []);
        setSkus(sk.data || []);
      } catch (e) {
        console.error(e);
      }
    })();
  }, []);

  async function submit() {
    setMsg("");
    if (!storeId || !skuId || !dateStr || !qty) {
      setMsg("Заполните магазин, SKU, дату и количество");
      return;
    }
    setBusy(true);
    try {
      await api.sales.addPromoterOne({
        store_id: Number(storeId),
        sku_id: Number(skuId),
        sold_at: dateStr,
        qty: Number(qty),
        amount: amount === "" ? undefined : Number(amount),
      });
      setMsg("Сохранено ✅");
      // сброс количества/суммы, оставим выбранные магазин и SKU
      setQty("");
      setAmount("");
    } catch (e: any) {
      setMsg(e?.response?.data?.detail || e?.message || "Ошибка сохранения");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 720, margin: "20px auto" }}>
      <h2>Продажа (Promoter POS)</h2>
      <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 1fr" }}>
        <div style={{ gridColumn: "1 / 3" }}>
          <label>Магазин</label>
          <select
            value={storeId}
            onChange={(e) => setStoreId(e.target.value ? Number(e.target.value) : "")}
            style={{ width: "100%", padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          >
            <option value="">— выберите —</option>
            {stores.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} {s.city ? `· ${s.city}` : ""} {s.network ? `· ${s.network}` : ""}
              </option>
            ))}
          </select>
        </div>

        <div style={{ gridColumn: "1 / 3" }}>
          <label>SKU</label>
          <select
            value={skuId}
            onChange={(e) => setSkuId(e.target.value ? Number(e.target.value) : "")}
            style={{ width: "100%", padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          >
            <option value="">— выберите —</option>
            {skus.map((x) => (
              <option key={x.id} value={x.id}>
                {x.brand} {x.model}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Дата продажи</label>
          <input
            type="date"
            value={dateStr}
            onChange={(e) => setDateStr(e.target.value)}
            style={{ width: "100%", padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
        </div>
        <div>
          <label>Количество</label>
          <input
            type="number"
            min={1}
            value={qty}
            onChange={(e) => setQty(e.target.value === "" ? "" : Number(e.target.value))}
            style={{ width: "100%", padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
        </div>
        <div>
          <label>Сумма (опционально)</label>
          <input
            type="number"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value === "" ? "" : Number(e.target.value))}
            placeholder="если пусто — возьмём из прайса"
            style={{ width: "100%", padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
        </div>
      </div>

      {msg && <div style={{ marginTop: 12, color: msg.includes("Ошибка") ? "crimson" : "green" }}>{msg}</div>}

      <div style={{ marginTop: 16 }}>
        <button
          onClick={submit}
          disabled={busy}
          style={{
            padding: "10px 14px",
            borderRadius: 10,
            border: "1px solid #ccc",
            background: busy ? "#f3f3f3" : "#fff",
            cursor: busy ? "not-allowed" : "pointer",
          }}
        >
          Сохранить
        </button>
      </div>
    </div>
  );
}
