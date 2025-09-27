import { api } from './http';

export async function superPlanReminder(params: { city?: string; month?: string }){
  const { data } = await api.get('/api/v1/plans/reminders/supervisor', { params });
  return data as { needs_plan: boolean; missing_count: number; city: string; month: string };
}
