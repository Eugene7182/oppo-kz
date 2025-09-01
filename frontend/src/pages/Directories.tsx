// frontend/src/pages/Directories.tsx
import { useEffect, useState } from "react";
import { api, Store, SKU } from "../shared/api/http";

export default function Directories() {
  // stores
  const [stores, setStores] = useState<Store[]>([]);
  const [sName, setSName] = useState("");
  const [sCity, setSCity] = useState("");
  const [sNet, setSNet] = useState("");

  // sku
  const [sku, setSku] = useState<SKU[]>([]);
  const [brand, setBrand] = useState("OPPO");
  const [model, setModel] = useState("");
  const [code, setCode] = useState("");

  // price
  const [priceSkuId, setPriceSkuId] = useState<number | "">("");
  const [price, setPrice] = useState<number | "">("");
  const [validFrom, setValidFrom] = useState<string>("");

  const [msg, setMsg] = useState("");

  async function load() {
    setMsg("");
    try {
      const [st, sk] = await Promise.all([api.refs.storesList(), api.refs.skuList()]);
      setStores(st);
      setSku(sk);
    } catch (e: any) {
      setMsg(e?.message || "Ошибка загрузки справочников");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function createStore() {
    setMsg("");
    try {
      await api.refs.storeCreate({
        name: sName.trim(),
        city: sCity.trim(),
        network: sNet.trim(),
      });
      setSName(""); setSCity(""); setSNet("");
      await load();
      setMsg("Магазин создан");
    } catch (e: any) {
      setMsg(e?.response?.data?.detail || e?.message || "Ошибка создания магазина");
    }
  }

  async function createSKU() {
    setMsg("");
    try {
      await api.refs.skuCreate({
        brand: brand.trim(),
        model: model.trim(),
        code: code.trim(),
      });
      setModel(""); setCode("");
      await load();
      setMsg("SKU создан");
    } catch (e: any) {
      setMsg(e?.response?.data?.detail || e?.message || "Ошибка создания SKU");
    }
  }

  async function createPrice() {
    setMsg("");
    if (priceSkuId === "" || price === "" || !validFrom) {
      setMsg("Укажи SKU, цену и дату начала");
      return;
    }
    try {
      await api.refs.priceCreate({
        sku_id: Number(priceSkuId),
        price: Number(price),
        valid_from: validFrom, // YYYY-MM-DD
      });
      setPriceSkuId(""); setPrice(""); setValidFrom("");
      setMsg("Цена добавлена");
    } catch (e: any) {
      setMsg(e?.response?.data?.detail || e?.message || "Ошибка создания цены");
    }
  }

  return (
    <div style={{ padding: 24, display: "grid", gap: 20 }}>
      <h2>Справочники</h2>

      {msg && <div style={{ color: msg.includes("Ошибка") ? "#b00020" : "#2b6" }}>{msg}</div>}

      {/* STORES */}
      <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
        <h3 style={{ marginTop: 0 }}>Магазины / Сети</h3>
        <div style={{ display: "grid", gap: 8, gridTemplateColumns: "1fr 1fr 1fr auto" }}>
          <input value={sName} onChange={(e) => setSName(e.target.value)} placeholder="Название магазина" style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }} />
          <input value={sCity} onChange={(e) => setSCity(e.target.value)} placeholder="Город" style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }} />
          <input value={sNet} onChange={(e) => setSNet(e.target.value)} placeholder="Сеть (например, Sulpak)" style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }} />
          <button onClick={createStore} style={{ borderRadius: 10, padding: "10px 16px" }}>Создать</button>
        </div>

        <div style={{ marginTop: 12, overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>ID</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>Название</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>Город</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>Сеть</th>
              </tr>
            </thead>
            <tbody>
              {stores.map((s) => (
                <tr key={s.id}>
                  <td style={{ padding: 6 }}>{s.id}</td>
                  <td style={{ padding: 6 }}>{s.name}</td>
                  <td style={{ padding: 6 }}>{s.city}</td>
                  <td style={{ padding: 6 }}>{s.network}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* SKU */}
      <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
        <h3 style={{ marginTop: 0 }}>SKU</h3>
        <div style={{ display: "grid", gap: 8, gridTemplateColumns: "1fr 1fr 1fr auto" }}>
          <input value={brand} onChange={(e) => setBrand(e.target.value)} placeholder="Бренд" style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }} />
          <input value={model} onChange={(e) => setModel(e.target.value)} placeholder="Модель" style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }} />
          <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="Код (внутренний, напр. OPPO-A38)" style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }} />
          <button onClick={createSKU} style={{ borderRadius: 10, padding: "10px 16px" }}>Создать</button>
        </div>

        <div style={{ marginTop: 12, overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>ID</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>Бренд</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>Модель</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee" }}>Код</th>
              </tr>
            </thead>
            <tbody>
              {sku.map((x) => (
                <tr key={x.id}>
                  <td style={{ padding: 6 }}>{x.id}</td>
                  <td style={{ padding: 6 }}>{x.brand}</td>
                  <td style={{ padding: 6 }}>{x.model}</td>
                  <td style={{ padding: 6 }}>{x.code}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* PRICE LIST */}
      <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
        <h3 style={{ marginTop: 0 }}>Прайс-лист</h3>
        <div style={{ display: "grid", gap: 8, gridTemplateColumns: "2fr 1fr 1fr auto", alignItems: "center" }}>
          <select
            value={priceSkuId}
            onChange={(e) => setPriceSkuId(e.target.value === "" ? "" : Number(e.target.value))}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
          >
            <option value="">— Выбери SKU —</option>
            {sku.map((x) => (
              <option value={x.id} key={x.id}>
                [{x.id}] {x.code} — {x.brand} {x.model}
              </option>
            ))}
          </select>
          <input
            type="number"
            value={price}
            onChange={(e) => setPrice(e.target.value === "" ? "" : Number(e.target.value))}
            placeholder="Цена"
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
          />
          <input
            type="date"
            value={validFrom}
            onChange={(e) => setValidFrom(e.target.value)}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
          />
          <button onClick={createPrice} style={{ borderRadius: 10, padding: "10px 16px" }}>
            Добавить цену
          </button>
        </div>
      </section>
    </div>
  );
}
