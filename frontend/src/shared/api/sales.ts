import { api } from './http';

export type SalePayload = {
  date?: string;
  store_id: string;
  sku_id: string;
  model?: string;
  memory_gb?: number;
  qty: number;
  price_per_unit?: number;
  network_id?: string;
};

export async function postSale(payload: SalePayload){
  const { data } = await api.post('/api/v1/promoter/sales', payload);
  return data as { ok: boolean };
}

export async function postZeroDay(dateISO?: string){
  const { data } = await api.post('/api/v1/promoter/sales/zero-day', { date: dateISO });
  return data as { ok: boolean };
}
