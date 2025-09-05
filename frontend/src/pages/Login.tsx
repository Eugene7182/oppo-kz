import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../shared/context/AuthContext';
import FormField from '../widgets/FormField';
import Spinner from '../widgets/Spinner';
import { useToast } from '../shared/ui/toast';

// Login page
export default function Login() {
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const from = (location.state as any)?.from?.pathname || '/';

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(username, password);
      navigate(from, { replace: true });
    } catch (e: any) {
      toast(e.message || 'Ошибка входа', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <form onSubmit={submit} className="bg-white p-6 rounded shadow w-80">
        <h1 className="text-xl mb-4">Вход</h1>
        <FormField label="Логин">
          <input
            className="w-full border px-2 py-1"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </FormField>
        <FormField label="Пароль">
          <input
            type="password"
            className="w-full border px-2 py-1"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </FormField>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50"
          disabled={loading}
        >
          {loading ? <Spinner /> : 'Войти'}
        </button>
      </form>
    </div>
  );
}
