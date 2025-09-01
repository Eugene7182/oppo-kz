import { api } from './http';

export type SalesLine = {
  date: string;
  store_id: string;
  sku_id: string;
  model?: string;
  memory_gb?: number;
  qty: number;
  revenue?: number;
  network_id?: string;
  promoter?: string;
};

export async function listSales(params: { date: string; store_id?: string; promoter_username?: string }){
  const { data } = await api.get('/api/v1/sales/list', { params });
  return data as { rows: SalesLine[] };
}

export async function upsertSale(payload: {
  date: string; store_id: string; sku_id: string; model?: string; memory_gb?: number; qty: number; price_per_unit?: number; network_id?: string; promoter_username?: string;
}){
  const { data } = await api.put('/api/v1/sales/upsert', payload);
  return data as { ok: boolean };
}

export async function deleteSale(params: { date: string; store_id: string; sku_id: string; memory_gb?: number; promoter_username?: string }){
  const { data } = await api.delete('/api/v1/sales', { params });
  return data as { ok: boolean };
}
