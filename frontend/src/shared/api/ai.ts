import { api } from './http';

export async function fetchReplenish(params: {days?: number; leadtime?: number; target_days?: number; min_qty?: number; same_city_only?: boolean; same_network_only?: boolean} = {}) {
  const { data } = await api.get('/api/v1/ai/reco/replenish', { params });
  return data as { items: any[] };
}

export async function fetchTransfer(params: {days?: number; leadtime?: number; target_days?: number; min_qty?: number; same_city_only?: boolean; same_network_only?: boolean} = {}) {
  const { data } = await api.get('/api/v1/ai/reco/transfer', { params });
  return data as { pairs: any[] };
}

export async function fetchAnomalies() {
  const { data } = await api.get('/api/v1/ai/alerts/anomalies');
  return data as { items: any[] };
}
