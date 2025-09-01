import { api } from './http';

export async function setPlan(payload: { store_id: string; month: string; plan_qty: number }) {
  const { data } = await api.post('/api/v1/plans', payload);
  return data;
}
export async function getPlansCity(params: { city: string; month: string }) {
  const { data } = await api.get('/api/v1/plans/city', { params });
  return data as { rows: any[] };
}
export async function getPlansAll(params: { month: string }) {
  const { data } = await api.get('/api/v1/plans/all', { params });
  return data as { rows: any[] };
}
