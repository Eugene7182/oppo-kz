import { useEffect, useState } from "react";
import { api } from "../shared/api/http";

type Grid = {
  id: number;
  sku_id?: number | null;
  network?: string | null;
  qty_from?: number | null;
  bonus_per_unit: number;
  valid_from: string;
  valid_to?: string | null;
};

type SKU = { id: number; brand: string; model: string; code: string };

export default function BonusGrids() {
  const [items, setItems] = useState<Grid[]>([]);
  const [skus, setSkus] = useState<SKU[]>([]);
  const [filterNetwork, setFilterNetwork] = useState("");
  const [filterSkuId, setFilterSkuId] = useState<number | "">("");
  const [activeOn, setActiveOn] = useState<string>("");

  // форма
  const [skuId, setSkuId] = useState<number | "">("");
  const [network, setNetwork] = useState("");
  const [qtyFrom, setQtyFrom] = useState<number | "">("");
  const [bonus, setBonus] = useState<number | "">("");
  const [from, setFrom] = useState<string>(() => new Date().toISOString().slice(0, 10));
  const [to, setTo] = useState<string>("");

  async function load() {
    const params: any = {};
    if (filterNetwork) params.network = filterNetwork;
    if (filterSkuId) params.sku_id = filterSkuId;
    if (activeOn) params.active_on = activeOn;
    const { data } = await api.bonus.list(params);
    setItems(data || []);
  }

  useEffect(() => {
    (async () => {
      const res = await api.sku.list();
      setSkus(res.data || []);
      await load();
    })();
  }, []);

  async function applyFilter() {
    await load();
  }

  async function add() {
    if (!bonus || !from) return;
    if (!skuId && !network) {
      alert("Укажите sku_id или network");
      return;
    }
    const body = {
      sku_id: skuId === "" ? null : Number(skuId),
      network: network || null,
      qty_from: qtyFrom === "" ? null : Number(qtyFrom),
      bonus_per_unit: Number(bonus),
      valid_from: from,
      valid_to: to || null,
    };
    await api.bonus.create(body);
    // сброс
    setSkuId("");
    setNetwork("");
    setQtyFrom("");
    setBonus("");
    setFrom(new Date().toISOString().slice(0, 10));
    setTo("");
    await load();
  }

  async function del(id: number) {
    if (!confirm("Удалить сетку?")) return;
    await api.bonus.remove(id);
    await load();
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Бонусные сетки</h2>

      {/* фильтры */}
      <div style={{ display: "grid", gap: 8, gridTemplateColumns: "1fr 1fr 1fr auto", marginTop: 8 }}>
        <input
          placeholder="Фильтр: Network"
          value={filterNetwork}
          onChange={(e) => setFilterNetwork(e.target.value)}
          style={{ padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
        />
        <select
          value={filterSkuId}
          onChange={(e) => setFilterSkuId(e.target.value ? Number(e.target.value) : "")}
          style={{ padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
        >
          <option value="">SKU: все</option>
          {skus.map((s) => (
            <option key={s.id} value={s.id}>
              {s.brand} {s.model}
            </option>
          ))}
        </select>
        <input
          type="date"
          value={activeOn}
          onChange={(e) => setActiveOn(e.target.value)}
          style={{ padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
        />
        <button
          onClick={applyFilter}
          style={{ border: "1px solid #ccc", background: "#fff", borderRadius: 8, padding: "8px 12px", cursor: "pointer" }}
        >
          Применить
        </button>
      </div>

      {/* форма создания */}
      <div style={{ marginTop: 16, padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
        <h4 style={{ margin: "0 0 8px 0" }}>Новая сетка</h4>
        <div style={{ display: "grid", gap: 8, gridTemplateColumns: "1fr 1fr 1fr 1fr 1fr 1fr auto" }}>
          <select
            value={skuId}
            onChange={(e) => setSkuId(e.target.value ? Number(e.target.value) : "")}
            style={{ padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          >
            <option value="">SKU (опц.)</option>
            {skus.map((s) => (
              <option key={s.id} value={s.id}>
                {s.brand} {s.model}
              </option>
            ))}
          </select>
          <input
            placeholder="Network (опц.)"
            value={network}
            onChange={(e) => setNetwork(e.target.value)}
            style={{ padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
          <input
            type="number"
            placeholder="От кол-ва (опц.)"
            value={qtyFrom}
            onChange={(e) => setQtyFrom(e.target.value === "" ? "" : Number(e.target.value))}
            style={{ padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
          <input
            type="number"
            step="0.01"
            placeholder="Бонус за шт."
            value={bonus}
            onChange={(e) => setBonus(e.target.value === "" ? "" : Number(e.target.value))}
            style={{ padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
          <input
            type="date"
            value={from}
            onChange={(e) => setFrom(e.target.value)}
            style={{ padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
          <input
            type="date"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            style={{ padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
          <button
            onClick={add}
            style={{ border: "1px solid #ccc", background: "#fff", borderRadius: 8, padding: "8px 12px", cursor: "pointer" }}
          >
            Добавить
          </button>
        </div>
        <div style={{ marginTop: 6, color: "#666" }}>
          Укажи хотя бы <b>SKU</b> или <b>Network</b>. Период действия: c <i>valid_from</i> по <i>valid_to</i> (если пусто — без
          окончания).
        </div>
      </div>

      {/* список */}
      <div style={{ marginTop: 16 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left", borderBottom: "1px solid #eee", padding: 8 }}>ID</th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #eee", padding: 8 }}>SKU</th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #eee", padding: 8 }}>Network</th>
              <th style={{ textAlign: "right", borderBottom: "1px solid #eee", padding: 8 }}>От кол-ва</th>
              <th style={{ textAlign: "right", borderBottom: "1px solid #eee", padding: 8 }}>Бонус / шт</th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #eee", padding: 8 }}>Период</th>
              <th style={{ borderBottom: "1px solid #eee", padding: 8 }} />
            </tr>
          </thead>
          <tbody>
            {items.map((g) => {
              const skuTitle =
                g.sku_id && skus.find((s) => s.id === g.sku_id)
                  ? `${skus.find((s) => s.id === g.sku_id)!.brand} ${skus.find((s) => s.id === g.sku_id)!.model}`
                  : "";
              return (
                <tr key={g.id}>
                  <td style={{ padding: 8 }}>{g.id}</td>
                  <td style={{ padding: 8 }}>{skuTitle}</td>
                  <td style={{ padding: 8 }}>{g.network || ""}</td>
                  <td style={{ padding: 8, textAlign: "right" }}>{g.qty_from ?? ""}</td>
                  <td style={{ padding: 8, textAlign: "right" }}>{g.bonus_per_unit}</td>
                  <td style={{ padding: 8 }}>
                    {g.valid_from} {g.valid_to ? `— ${g.valid_to}` : ""}
                  </td>
                  <td style={{ padding: 8, textAlign: "right" }}>
                    <button
                      onClick={() => del(g.id)}
                      style={{ border: "1px solid #ccc", background: "#fff", borderRadius: 8, padding: "6px 10px", cursor: "pointer" }}
                    >
                      ❌
                    </button>
                  </td>
                </tr>
              );
            })}
            {items.length === 0 && (
              <tr>
                <td colSpan={7} style={{ padding: 12, color: "#777" }}>
                  Пусто
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
