import { useMemo, useState } from "react";

import { salesMock } from "../../../entities/sale/mock";
import { products as productMock } from "../../../entities/product/mock";
import { dictionariesMock } from "../../../entities/dict/mock";
import { bonusPayoutsMock } from "../../../entities/bonus/mock";
import { createId } from "../../../shared/lib/createId";
import type { Sale } from "../../../entities/sale";
import type { Product } from "../../../entities/product";
import type { StoreDictItem } from "../../../entities/dict";

export type SalesMockWithId = Sale;

type ConflictResult =
  | { type: "updated"; sale: SalesMockWithId }
  | { type: "conflict"; server: SalesMockWithId; local: SalesMockWithId };

type BonusSummary = {
  monthTotal: number;
  plan: number;
  fact: number;
  achv: number;
  averageAmount: number;
};

type UsePromoterData = {
  sales: SalesMockWithId[];
  products: Product[];
  stores: StoreDictItem[];
  bonusSummary: BonusSummary;
  corrections: { saleId: string; deltaQty: number; reason: string; createdAt: string }[];
  updateSale: (id: string, update: Partial<SalesMockWithId>, force?: boolean) => ConflictResult | null;
  deleteSale: (id: string) => void;
  addSale: (values: { storeId: string; skuId: string; qty: number; soldAt: string }) => void;
  addCorrection: (correction: { saleId: string; deltaQty: number; reason: string; createdAt: string }) => void;
};

export function usePromoterData(): UsePromoterData {
  const [sales, setSales] = useState<SalesMockWithId[]>(salesMock);
  const [corrections, setCorrections] = useState<UsePromoterData["corrections"]>([]);

  const products = productMock;
  const stores = dictionariesMock.stores;

  const bonusSummary = useMemo<BonusSummary>(() => {
    const monthTotal = bonusPayoutsMock.reduce((acc, item) => acc + item.amount, 0);
    const fact = sales.reduce((acc, sale) => acc + sale.qty, 0);
    const plan = 450;
    const achv = Math.round((fact / plan) * 100);
    const totalAmount = sales.reduce((acc, sale) => acc + sale.amount, 0);
    const averageAmount = sales.length ? Math.round(totalAmount / sales.length) : 0;
    return { monthTotal, plan, fact, achv, averageAmount };
  }, [sales]);

  function addSale(values: { storeId: string; skuId: string; qty: number; soldAt: string }) {
    const product = products.find((item) => item.id === values.skuId);
    const store = stores.find((item) => item.id === values.storeId);
    if (!product || !store) return;
    const amount = product.price * values.qty;
    const newSale: SalesMockWithId = {
      id: createId(),
      storeId: store.id,
      storeName: store.name,
      network: product.series,
      skuId: product.id,
      skuName: product.model,
      soldAt: values.soldAt,
      qty: values.qty,
      amount,
      promoterId: "u-promoter",
      status: "draft",
      version: 1,
    };
    setSales((prev) => [newSale, ...prev]);
  }

  function updateSale(id: string, update: Partial<SalesMockWithId>, force = false): ConflictResult | null {
    const current = sales.find((sale) => sale.id === id);
    if (!current) return null;
    if (current.status === "locked" && !force) {
      return {
        type: "conflict",
        server: current,
        local: { ...current, ...update, version: current.version },
      };
    }

    const next = { ...current, ...update } as SalesMockWithId;
    setSales((prev) => prev.map((sale) => (sale.id === id ? next : sale)));
    return { type: "updated", sale: next };
  }

  function deleteSale(id: string) {
    setSales((prev) => prev.filter((sale) => sale.id !== id));
  }

  function addCorrection(correction: { saleId: string; deltaQty: number; reason: string; createdAt: string }) {
    setCorrections((prev) => [correction, ...prev]);
  }

  return {
    sales,
    products,
    stores,
    bonusSummary,
    corrections,
    updateSale,
    deleteSale,
    addSale,
    addCorrection,
  };
}
