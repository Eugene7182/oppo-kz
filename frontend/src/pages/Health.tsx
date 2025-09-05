import React, { useEffect, useState } from 'react';
import http from '../lib/http';
import Spinner from '../components/Spinner';
import { useToast } from '../lib/toast';

interface HealthInfo {
  health: string | null;
  version: string | null;
  db: string | null;
}

// Страница проверки состояния API
export default function Health() {
  const [info, setInfo] = useState<HealthInfo>({
    health: null,
    version: null,
    db: null,
  });
  const toast = useToast();

  useEffect(() => {
    // Запрашиваем все три эндпойнта параллельно
    Promise.all([
      http.get('/api/v1/health').catch(() => ({ data: { status: 'fail' } })),
      http.get('/api/v1/version').catch(() => ({ data: { version: 'fail' } })),
      http
        .get('/api/v1/db_status')
        .catch(() => ({ data: { status: 'fail' } })),
    ])
      .then(([h, v, d]) =>
        setInfo({ health: h.data.status, version: v.data.version, db: d.data.status })
      )
      .catch(() => toast('Сервер недоступен', 'error'));
  }, [toast]);

  if (!info.health || !info.version || !info.db) return <Spinner />;

  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Card title="Health" ok={info.health === 'ok'} value={info.health} />
      <Card title="Version" ok={!!info.version} value={info.version} />
      <Card title="DB" ok={info.db === 'ok'} value={info.db} />
    </div>
  );
}

// Простая карточка статуса
function Card({
  title,
  ok,
  value,
}: {
  title: string;
  ok: boolean;
  value: string | null;
}) {
  return (
    <div
      className={`p-4 rounded shadow text-center ${
        ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
      }`}
    >
      <div className="font-semibold">{title}</div>
      <div className="mt-2 text-sm">{value}</div>
    </div>
  );
}
