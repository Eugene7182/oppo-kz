// frontend/src/pages/PromoterSale.tsx
import { useEffect, useState } from "react";
import { api, Store, SKU } from "../shared/api/http";

export default function PromoterSale() {
  const [stores, setStores] = useState<Store[]>([]);
  const [sku, setSku] = useState<SKU[]>([]);
  const [date, setDate] = useState<string>("");
  const [storeId, setStoreId] = useState<number | "">("");
  const [skuId, setSkuId] = useState<number | "">("");
  const [qty, setQty] = useState<number | "">("");
  const [amount, setAmount] = useState<number | "">("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [st, sk] = await Promise.all([api.refs.storesList(), api.refs.skuList()]);
        setStores(st);
        setSku(sk);
      } catch (e: any) {
        setMsg(e?.message || "Ошибка загрузки справочников");
      }
    })();
  }, []);

  async function submit() {
    setMsg("");
    if (!date || storeId === "" || skuId === "" || qty === "") {
      setMsg("Заполни дату, магазин, SKU и количество");
      return;
    }
    try {
      await api.sales.addPromoterOne({
        date,
        store_id: Number(storeId),
        sku_id: Number(skuId),
        qty: Number(qty),
        amount: amount === "" ? undefined : Number(amount),
      });
      setMsg("Продажа записана");
      setQty(""); setAmount("");
    } catch (e: any) {
      setMsg(e?.response?.data?.detail || e?.message || "Ошибка сохранения");
    }
  }

  return (
    <div style={{ padding: 24, display: "grid", gap: 12 }}>
      <h2>Продажа (промоутер)</h2>

      {msg && (
        <div style={{ color: msg.includes("Ошибка") ? "#b00020" : "#2b6" }}>{msg}</div>
      )}

      <div style={{ display: "grid", gap: 10, gridTemplateColumns: "1fr 1fr" }}>
        <label>
          Дата
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)}
                 style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ddd", marginTop: 6 }} />
        </label>

        <label>
          Магазин
          <select value={storeId} onChange={(e) => setStoreId(e.target.value === "" ? "" : Number(e.target.value))}
                  style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ddd", marginTop: 6 }}>
            <option value="">— выбери магазин —</option>
            {stores.map((s) => (
              <option key={s.id} value={s.id}>
                [{s.id}] {s.network} / {s.city} / {s.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          SKU
          <select value={skuId} onChange={(e) => setSkuId(e.target.value === "" ? "" : Number(e.target.value))}
                  style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ddd", marginTop: 6 }}>
            <option value="">— выбери SKU —</option>
            {sku.map((x) => (
              <option key={x.id} value={x.id}>
                [{x.id}] {x.code} — {x.brand} {x.model}
              </option>
            ))}
          </select>
        </label>

        <label>
          Количество
          <input type="number" min={1} value={qty}
                 onChange={(e) => setQty(e.target.value === "" ? "" : Number(e.target.value))}
                 style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ddd", marginTop: 6 }} />
        </label>

        <label>
          Сумма (необязательно)
          <input type="number" min={0} value={amount}
                 onChange={(e) => setAmount(e.target.value === "" ? "" : Number(e.target.value))}
                 placeholder="если пусто — посчитаем по прайсу"
                 style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ddd", marginTop: 6 }} />
        </label>
      </div>

      <div>
        <button onClick={submit} style={{ padding: "10px 16px", borderRadius: 10 }}>
          Сохранить
        </button>
      </div>
    </div>
  );
}
