import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import http, { setAuthTokens, clearAuthTokens } from '../lib/http';
import { toast } from '../lib/toast';

export type Role = 'admin' | 'office' | 'supervisor' | 'promoter';

export interface User {
  username: string;
  role: Role;
}

interface AuthContextType {
  access: string | null;
  refresh: string | null;
  me: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  refreshToken: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  access: null,
  refresh: null,
  me: null,
  loading: true,
  login: async () => {
    throw new Error('AuthProvider not ready');
  },
  refreshToken: async () => {
    throw new Error('AuthProvider not ready');
  },
  logout: () => {
    throw new Error('AuthProvider not ready');
  },
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [access, setAccess] = useState<string | null>(
    () => localStorage.getItem('accessToken')
  );
  const [refresh, setRefresh] = useState<string | null>(
    () => localStorage.getItem('refreshToken')
  );
  const [me, setMe] = useState<User | null>(() => {
    const stored = localStorage.getItem('me');
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(true);

  // Helper to persist tokens both in memory and localStorage
  const persistTokens = (a: string, r: string) => {
    setAuthTokens(a, r);
    setAccess(a);
    setRefresh(r);
    localStorage.setItem('accessToken', a);
    localStorage.setItem('refreshToken', r);
  };

  // Try to restore user on mount
  useEffect(() => {
    if (access && refresh && !me) {
      http
        .get('/api/v1/auth/me')
        .then((res) => {
          setMe(res.data);
          localStorage.setItem('me', JSON.stringify(res.data));
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Perform login, try JSON first and fallback to form
  const login = async (username: string, password: string) => {
    try {
      const { data } = await http.post('/api/v1/auth/login', {
        username,
        password,
      });
      persistTokens(data.access_token, data.refresh_token);
    } catch (err: any) {
      if (err.response?.status === 415) {
        const body = new URLSearchParams();
        body.append('username', username);
        body.append('password', password);
        const { data } = await http.post('/api/v1/auth/login', body, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        persistTokens(data.access_token, data.refresh_token);
      } else {
        toast('Не удалось войти', 'error');
        throw err;
      }
    }

    try {
      const meRes = await http.get('/api/v1/auth/me');
      setMe(meRes.data);
      localStorage.setItem('me', JSON.stringify(meRes.data));
    } catch {
      toast('Не удалось получить профиль', 'error');
    }
  };

  // Manual refresh token call
  const refreshToken = async () => {
    if (!refresh) return;
    try {
      const { data } = await http.post('/api/v1/auth/refresh', {
        refresh_token: refresh,
      });
      persistTokens(data.access_token, data.refresh_token);
    } catch {
      logout();
    }
  };

  // Clear all auth data
  const logout = () => {
    clearAuthTokens();
    setAccess(null);
    setRefresh(null);
    setMe(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('me');
  };

  return (
    <AuthContext.Provider
      value={{ access, refresh, me, loading, login, refreshToken, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

