import { api } from './http';

export async function listNetworks(){
  const { data } = await api.get('/api/v1/bonus/networks');
  return data as { networks: string[] };
}
export async function fetchBonusGrid(network_id: string, month?: string){
  const { data } = await api.get('/api/v1/bonus/grid', { params: { network_id, month } });
  return data as { items: { sku_id: string; model: string; amount: number }[] };
}
export async function saveBonusGrid(network_id: string, items: { sku_id: string; amount: number }[], month?: string){
  const { data } = await api.post('/api/v1/bonus/grid', { network_id, items, month });
  return data as { ok: boolean };
}
