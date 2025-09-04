
import { useEffect, useState } from 'react'
import { http } from '../shared/http'
import DataTable from '../components/DataTable'

type Job = { id:number; status:string; progress:number; processed:number; total:number; error?:string; type:string; filename:string; created_at:string; updated_at:string; has_payload:boolean }

export default function ImportsPage() {
  const [file, setFile] = useState<File | null>(null)
  const [source, setSource] = useState<'network'|'promoters'>('network')
  const [job, setJob] = useState<Job | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<Job[]>([])
  const [filters, setFilters] = useState({ status:'', type:'' })

  async function start() {
    if (!file) return
    setError(null); setJob(null)
    const form = new FormData()
    form.append('file', file)
    const { data } = await http.post(`/api/v1/imports/sales/${source}`, form)
    setJob({ id: data.job_id, status: data.status, progress: 0, processed:0, total:0, type:'sales_'+source, filename:file.name, created_at:'', updated_at:'', has_payload:true })
    loadHistory()
  }

  async function loadHistory() {
    const params:any = {}
    if (filters.status) params.status = filters.status
    if (filters.type) params.type = filters.type
    const { data } = await http.get('/api/v1/imports', { params })
    setHistory(data.items)
  }
  useEffect(()=>{ loadHistory() }, [filters.status, filters.type])

  useEffect(()=>{
    if (!job?.id) return
    const int = setInterval(async () => {
      try {
        const { data } = await http.get(`/api/v1/imports/${job.id}`)
        setJob(data)
        loadHistory()
        if (data.status === 'done' || data.status === 'error') {
          clearInterval(int)
        }
      } catch (e:any) {
        setError(e?.response?.data?.detail || e?.message || 'Ошибка опроса')
        clearInterval(int)
      }
    }, 1000)
    return () => clearInterval(int)
  }, [job?.id])

  async function retry(id: number) {
    const { data } = await http.post(`/api/v1/imports/${id}/retry`, {})
    setJob({ id: data.job_id, status: data.status, progress: 0, processed:0, total:0, type:'', filename:'', created_at:'', updated_at:'', has_payload:true })
  }

  return (
    <div>
      <h2>Импорты</h2>
      <div style={{ display:'flex', gap:8, alignItems:'center', marginBottom:12, flexWrap:'wrap' }}>
        <select value={source} onChange={e=>setSource(e.target.value as any)}>
          <option value="network">Продажи сетей (CSV)</option>
          <option value="promoters">Продажи промоутеров (CSV)</option>
        </select>
        <input type="file" accept=".csv" onChange={e=>setFile(e.target.files?.[0] || null)} />
        <button onClick={start} disabled={!file}>Запустить импорт</button>
      </div>
      {error && <div style={{ color:'crimson' }}>{error}</div>}
      {job && (
        <div style={{ marginTop:12, padding:12, border:'1px solid #eee', borderRadius:8 }}>
          <div><b>Job #{job.id}</b> — {job.status}</div>
          <div style={{ marginTop:8, width:'100%', background:'#eee', height:14, borderRadius:8, overflow:'hidden' }}>
            <div style={{ width:`${job.progress}%`, height:'100%', background:'#3b82f6' }} />
          </div>
          <div style={{ marginTop:6, fontSize:12 }}>{job.processed}/{job.total} ({job.progress}%)</div>
          {job.error && <div style={{ color:'crimson', marginTop:6 }}>{job.error}</div>}
        </div>
      )}

      <h3 style={{ marginTop:24 }}>История</h3>
      <div style={{ display:'flex', gap:8, alignItems:'center', marginBottom:8 }}>
        <select value={filters.status} onChange={e=>setFilters({ ...filters, status: e.target.value })}>
          <option value="">Все статусы</option>
          <option value="queued">queued</option>
          <option value="running">running</option>
          <option value="done">done</option>
          <option value="error">error</option>
        </select>
        <select value={filters.type} onChange={e=>setFilters({ ...filters, type: e.target.value })}>
          <option value="">Все типы</option>
          <option value="sales_network">sales_network</option>
          <option value="sales_promoters">sales_promoters</option>
        </select>
        <button onClick={loadHistory}>Обновить</button>
      </div>
      <DataTable rows={history} columns={[
        { key:'id', title:'ID' },
        { key:'type', title:'Тип' },
        { key:'filename', title:'Файл' },
        { key:'status', title:'Статус' },
        { key:'progress', title:'%' },
        { key:'processed', title:'Обработано' },
        { key:'total', title:'Всего' },
        { key:'created_at', title:'Создан' },
        { key:'updated_at', title:'Обновлён' },
      ]}/>
      <ul>
        {history.map(j => (
          <li key={j.id}>
            #{j.id} — {j.status} — {j.filename}
            <button style={{ marginLeft:8 }} disabled={!j.has_payload} onClick={()=>retry(j.id)}>Retry</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
