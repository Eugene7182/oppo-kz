import { useEffect, useState } from 'react'
import { http } from '@/shared/http'

export default function HealthPage() {
  const [status, setStatus] = useState('checking...')
  const [version, setVersion] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    (async () => {
      try {
        const [h, v] = await Promise.all([
          http.get('/api/v1/health'),
          http.get('/api/v1/version'),
        ])
        setStatus(h.status === 200 ? 'OK' : `HTTP ${h.status}`)
        setVersion(v.data)
      } catch (e: any) {
        setError(e?.message ?? 'request failed')
      }
    })()
  }, [])

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">API Health</h1>
      <div className="mb-2">Status: <b>{status}</b></div>
      {version && (
        <pre className="bg-gray-900 text-gray-100 p-3 rounded text-sm overflow-auto">
{JSON.stringify(version, null, 2)}
        </pre>
      )}
      {error && <div className="mt-2 text-red-600">Error: {error}</div>}
      <div className="mt-4 text-sm text-gray-500">
        Base URL: {import.meta.env.VITE_API_URL}
      </div>
    </div>
  )
}
