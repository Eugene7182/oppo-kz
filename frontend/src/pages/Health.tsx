import React, { useEffect, useState } from 'react';
import http from '../lib/http';
import Spinner from '../components/Spinner';
import { useToast } from '../lib/toast';

// Health check page
export default function Health() {
  const [status, setStatus] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    http
      .get('/health')
      .then((res) => setStatus(res.data.status))
      .catch(() => {
        setStatus('error');
        toast('Сервер недоступен', 'error');
      });
  }, [toast]);

  if (!status) return <Spinner />;

  return <div>Server status: {status}</div>;
}
