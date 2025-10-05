import { FormEvent, useState } from "react";
import { Calendar, Save } from "lucide-react";

import type { Product } from "../../entities/product";
import type { StoreDictItem } from "../../entities/dict";

export type SaleFormValues = {
  storeId: string;
  skuId: string;
  qty: number;
  soldAt: string;
};

export function SalesForm({ products, stores, onSubmit }: { products: Product[]; stores: StoreDictItem[]; onSubmit: (values: SaleFormValues) => void }) {
  const [values, setValues] = useState<SaleFormValues>({ storeId: stores[0]?.id ?? "", skuId: products[0]?.id ?? "", qty: 1, soldAt: new Date().toISOString().slice(0, 10) });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Магазин</label>
          <select
            className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            value={values.storeId}
            onChange={(event) => setValues((prev) => ({ ...prev, storeId: event.target.value }))}
          >
            {stores.map((store) => (
              <option key={store.id} value={store.id}>
                {store.name} · {store.city}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Модель</label>
          <select
            className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            value={values.skuId}
            onChange={(event) => setValues((prev) => ({ ...prev, skuId: event.target.value }))}
          >
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.model} · {product.price.toLocaleString()} ₸
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Количество</label>
          <input
            type="number"
            min={0}
            className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            value={values.qty}
            onChange={(event) => setValues((prev) => ({ ...prev, qty: Number(event.target.value) }))}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Дата</label>
          <div className="mt-1 flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm">
            <Calendar size={16} className="text-slate-500" />
            <input
              type="date"
              className="flex-1 bg-transparent outline-none"
              value={values.soldAt}
              onChange={(event) => setValues((prev) => ({ ...prev, soldAt: event.target.value }))}
            />
          </div>
        </div>
      </div>
      <button
        type="submit"
        className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-slate-900/30 transition hover:bg-slate-800"
      >
        <Save size={16} /> Сохранить продажу
      </button>
    </form>
  );
}
