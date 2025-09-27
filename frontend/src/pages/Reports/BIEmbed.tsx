    import React, { useEffect, useState } from 'react';

    export default function BIEmbed() {
      const [dashboardId, setDashboardId] = useState<string>('1');
      const [regionId, setRegionId] = useState<string>('');
      const [storeId, setStoreId] = useState<string>('');
      const [url, setUrl] = useState<string>('');

      async function load() {
        const qs = new URLSearchParams();
        if (dashboardId) qs.set('dashboard_id', dashboardId);
        if (regionId) qs.set('region_id', regionId);
        if (storeId) qs.set('store_id', storeId);
        const res = await fetch(`/api/v1/bi/embed/dashboard?${qs.toString()}`);
        if (!res.ok) { setUrl(''); return; }
        const data = await res.json();
        setUrl(data.url);
      }

      useEffect(() => { load(); }, []);

      return (
        <div className="p-4 space-y-3 h-full flex flex-col">
          <h1 className="text-xl font-semibold">BI Дашборды</h1>
          <div className="flex flex-wrap gap-2 items-end">
            <label className="block">
              <div className="text-sm">Dashboard ID</div>
              <input className="border p-1 w-40" value={dashboardId} onChange={e => setDashboardId(e.target.value)} />
            </label>
            <label className="block">
              <div className="text-sm">Region ID (опц.)</div>
              <input className="border p-1 w-40" value={regionId} onChange={e => setRegionId(e.target.value)} />
            </label>
            <label className="block">
              <div className="text-sm">Store ID (опц.)</div>
              <input className="border p-1 w-40" value={storeId} onChange={e => setStoreId(e.target.value)} />
            </label>
            <button className="btn" onClick={load}>Показать</button>
          </div>
          <div className="flex-1 min-h-[60vh] border rounded overflow-hidden">
            {url ? (
              <iframe title="Metabase Dashboard" src={url} style={{ width: '100%', height: '100%', border: 0 }} />
            ) : (
              <div className="p-4 text-sm text-gray-600">Укажите Dashboard ID и нажмите «Показать».</div>
            )}
          </div>
        </div>
      );
    }
    