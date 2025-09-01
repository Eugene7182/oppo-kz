import { api } from './http';
export async function kpiCity(city?: string, month?: string){
  const { data } = await api.get('/api/v1/kpi/city', { params: { city, month } });
  return data as { city: string; month: string; plan: number; fact: number; progress: number; stores: any[] };
}
export async function kpiOffice(month?: string){
  const { data } = await api.get('/api/v1/kpi/office', { params: { month } });
  return data as { month: string; plan: number; fact: number; progress: number; cities: any[] };
}
