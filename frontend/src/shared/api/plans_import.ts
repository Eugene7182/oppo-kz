import { api } from './http';

export async function importPlansCSV(file: File, monthISO: string){
  const form = new FormData();
  form.append('file', file);
  form.append('month', monthISO);
  const { data } = await api.post('/api/v1/plans/import', form, { headers: { 'Content-Type': 'multipart/form-data' } });
  return data as { ok: boolean; imported: number };
}
