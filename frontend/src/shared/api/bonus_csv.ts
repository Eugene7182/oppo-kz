import { api } from './http';
export async function exportBonusCSV(network_id: string, month?: string){
  const { data } = await api.get('/api/v1/bonus/grid/export', { params: { network_id, month }, responseType: 'blob' as any });
  return data as Blob;
}
export async function importBonusCSV(file: File, network_id: string, month?: string){
  const form = new FormData();
  form.append('file', file);
  form.append('network_id', network_id);
  if (month) form.append('month', month);
  const { data } = await api.post('/api/v1/bonus/grid/import', form, { headers: { 'Content-Type': 'multipart/form-data' } });
  return data as { ok: boolean; imported: number };
}
