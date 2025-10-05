import { useEffect, useState } from "react";
import { SlidersHorizontal, FilterX } from "lucide-react";

import { ModalSheet } from "../ModalSheet";
import type { Product } from "../../entities/product";

export type FilterState = {
  scope: "all" | "network" | "store" | "region" | "team";
  period: { preset: "mtd" | "qtd" | "ytd" | "custom"; from: string; to: string };
  timeGrain: "day" | "week" | "month";
  models: string[];
  metric: "qty" | "revenue" | "achv" | "bonus";
  compare: "none" | "wow" | "mom" | "yoy" | "lfl";
};

const DEFAULT_FILTERS: FilterState = {
  scope: "all",
  period: { preset: "mtd", from: "", to: "" },
  timeGrain: "week",
  models: [],
  metric: "qty",
  compare: "none",
};

export function FilterBar({ products, onChange }: { products: Product[]; onChange: (filters: FilterState) => void }) {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    onChange(DEFAULT_FILTERS);
  }, [onChange]);

  function apply(next: FilterState) {
    setFilters(next);
    onChange(next);
    setOpen(false);
  }

  function toggleModel(id: string) {
    setFilters((prev) => {
      const models = prev.models.includes(id) ? prev.models.filter((item) => item !== id) : [...prev.models, id];
      const next = { ...prev, models };
      onChange(next);
      return next;
    });
  }

  const sheet = (
    <div className="space-y-4 text-sm">
      <div>
        <label className="text-xs font-semibold uppercase text-slate-500">Scope</label>
        <select
          className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2"
          value={filters.scope}
          onChange={(event) => setFilters((prev) => ({ ...prev, scope: event.target.value as FilterState["scope"] }))}
        >
          <option value="all">Вся страна</option>
          <option value="network">По сети</option>
          <option value="region">По региону</option>
          <option value="store">По магазину</option>
          <option value="team">Моя команда</option>
        </select>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col gap-1">
          <span className="text-xs font-semibold uppercase text-slate-500">Period</span>
          <select
            value={filters.period.preset}
            onChange={(event) => setFilters((prev) => ({ ...prev, period: { ...prev.period, preset: event.target.value as FilterState["period"]["preset"] } }))}
            className="rounded-xl border border-slate-200 px-3 py-2"
          >
            <option value="mtd">MTD</option>
            <option value="qtd">QTD</option>
            <option value="ytd">YTD</option>
            <option value="custom">Custom</option>
          </select>
        </label>
        {filters.period.preset === "custom" && (
          <div className="grid grid-cols-2 gap-2">
            <input
              type="date"
              value={filters.period.from}
              onChange={(event) => setFilters((prev) => ({ ...prev, period: { ...prev.period, from: event.target.value } }))}
              className="rounded-xl border border-slate-200 px-3 py-2"
            />
            <input
              type="date"
              value={filters.period.to}
              onChange={(event) => setFilters((prev) => ({ ...prev, period: { ...prev.period, to: event.target.value } }))}
              className="rounded-xl border border-slate-200 px-3 py-2"
            />
          </div>
        )}
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col gap-1">
          <span className="text-xs font-semibold uppercase text-slate-500">Time grain</span>
          <select
            value={filters.timeGrain}
            onChange={(event) => setFilters((prev) => ({ ...prev, timeGrain: event.target.value as FilterState["timeGrain"] }))}
            className="rounded-xl border border-slate-200 px-3 py-2"
          >
            <option value="day">День</option>
            <option value="week">Неделя</option>
            <option value="month">Месяц</option>
          </select>
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-xs font-semibold uppercase text-slate-500">Metric</span>
          <select
            value={filters.metric}
            onChange={(event) => setFilters((prev) => ({ ...prev, metric: event.target.value as FilterState["metric"] }))}
            className="rounded-xl border border-slate-200 px-3 py-2"
          >
            <option value="qty">Шт.</option>
            <option value="revenue">₸</option>
            <option value="achv">Achv%</option>
            <option value="bonus">Bonus</option>
          </select>
        </label>
      </div>
      <div>
        <span className="text-xs font-semibold uppercase text-slate-500">Модели</span>
        <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {products.map((product) => (
            <label key={product.id} className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2">
              <input
                type="checkbox"
                checked={filters.models.includes(product.id)}
                onChange={() => toggleModel(product.id)}
              />
              <span className="text-sm text-slate-600">{product.model}</span>
            </label>
          ))}
        </div>
      </div>
      <div>
        <span className="text-xs font-semibold uppercase text-slate-500">Сравнение</span>
        <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
          {[
            { value: "none", label: "Без" },
            { value: "wow", label: "WoW" },
            { value: "mom", label: "MoM" },
            { value: "yoy", label: "YoY" },
            { value: "lfl", label: "LFL" },
          ].map((item) => (
            <button
              key={item.value}
              onClick={() => setFilters((prev) => ({ ...prev, compare: item.value as FilterState["compare"] }))}
              className={`rounded-full border px-3 py-2 font-medium transition ${
                filters.compare === item.value ? "border-slate-900 bg-slate-900 text-white" : "border-slate-200"
              }`}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <button
        onClick={() => apply(filters)}
        className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
      >
        Применить
      </button>
    </div>
  );

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-3xl border border-slate-200 bg-white px-4 py-3 text-xs">
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-3 py-2 text-white"
        type="button"
      >
        <SlidersHorizontal size={14} /> Фильтры
      </button>
      <div className="hidden flex-wrap items-center gap-2 lg:flex">
        <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-600">Scope: {filters.scope}</span>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-600">Metric: {filters.metric}</span>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-600">Compare: {filters.compare}</span>
      </div>
      <button
        onClick={() => apply(DEFAULT_FILTERS)}
        className="ml-auto inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-2 text-slate-500"
        type="button"
      >
        <FilterX size={14} /> Сбросить
      </button>
      <ModalSheet open={open} onClose={() => setOpen(false)} title="Фильтры BI">
        {sheet}
      </ModalSheet>
    </div>
  );
}
