import { api } from './http';

export async function fetchABCXYZ(params: {days?: number} = {}){
  const { data } = await api.get('/api/v1/ai/classify/abcxyz', { params });
  return data as { items: { sku_id: string; total_qty: number; ABC: string; XYZ: string }[] };
}

export async function fetchForecast(params: {group_by?: string; horizon_days?: number} = {}){
  const { data } = await api.get('/api/v1/ai/forecast/sales', { params });
  return data as { series: { date: string; key: string; qty: number }[], forecast: { date: string; key: string; qty: number }[] };
}
