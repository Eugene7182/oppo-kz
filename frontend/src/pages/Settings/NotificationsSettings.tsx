import React, { useEffect, useState } from 'react';
import { urlB64ToUint8Array } from '../../lib/base64url';

type Pref = {
  enable_time_reminders: boolean;
  times: string[] | null;
  saturday_cutoff_hour: number;
  enabled: boolean;
};

async function getPublicKey(): Promise<string> {
  const res = await fetch('/api/v1/notifications/push/public-key');
  const data = await res.json();
  return data.public_key;
}

async function ensurePush(): Promise<boolean> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return false;
  const perm = await Notification.requestPermission();
  if (perm !== 'granted') return false;
  const reg = await navigator.serviceWorker.ready;
  const publicKey = await getPublicKey();
  const sub = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlB64ToUint8Array(publicKey),
  });
  const payload = { endpoint: sub.endpoint, keys: (sub as any).toJSON().keys, user_agent: navigator.userAgent };
  await fetch('/api/v1/notifications/push/subscribe', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  return true;
}

export default function NotificationsSettings() {
  const [pref, setPref] = useState<Pref | null>(null);
  const [testing, setTesting] = useState(false);

  async function loadPref() {
    const res = await fetch('/api/v1/notifications/preferences');
    setPref(await res.json());
  }
  async function savePref() {
    await fetch('/api/v1/notifications/preferences', {
      method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(pref)
    });
    loadPref();
  }
  async function sendTest() {
    setTesting(true);
    await ensurePush();
    await fetch('/api/v1/notifications/push/test', { method: 'POST' });
    setTesting(false);
  }

  useEffect(() => { loadPref(); }, []);

  if (!pref) return <div className="p-4">Загрузка...</div>;

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-semibold">Настройки уведомлений</h1>
      <label className="flex items-center gap-2">
        <input type="checkbox" checked={!!pref.enabled} onChange={e => setPref({ ...pref, enabled: e.target.checked })} />
        Включить уведомления (внутри приложения)
      </label>
      <label className="flex items-center gap-2">
        <input type="checkbox" checked={!!pref.enable_time_reminders}
               onChange={e => setPref({ ...pref, enable_time_reminders: e.target.checked })} />
        Напоминания по времени (рабочие дни)
      </label>

      <div>
        <div className="text-sm text-gray-600 mb-1">Времена напоминаний (по умолчанию: 11:00, 12:00, 14:00, 16:00, 18:00)</div>
        <textarea className="w-full border p-2" rows={2}
          value={pref.times?.join(',') ?? ''}
          onChange={e => setPref({ ...pref, times: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })} />
      </div>

      <div>
        <label className="block text-sm">Субботний лимит (час, по умолчанию 16)</label>
        <input type="number" min={0} max={23} className="border p-1"
          value={pref.saturday_cutoff_hour} onChange={e => setPref({ ...pref, saturday_cutoff_hour: Number(e.target.value) })} />
      </div>

      <div className="border-t pt-3">
        <div className="text-sm">Web Push включается автоматически для этого устройства при нажатии кнопки ниже.</div>
        <button className="btn mt-2" onClick={sendTest} disabled={testing}>Включить и отправить тест</button>
      </div>

      <button className="btn" onClick={savePref}>Сохранить</button>
    </div>
  );
}
