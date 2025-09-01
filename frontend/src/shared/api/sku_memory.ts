import { api } from './http';

export async function listMemoryOptions(sku_id: string){
  const { data } = await api.get('/api/v1/skus/memory', { params: { sku_id } });
  return data as { items: number[] };
}
export async function saveMemoryOptions(sku_id: string, memory_options: number[]){
  const { data } = await api.post('/api/v1/skus/memory', { sku_id, memory_options });
  return data as { ok: boolean };
}
