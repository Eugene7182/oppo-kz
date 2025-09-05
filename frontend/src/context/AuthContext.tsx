import React, { createContext, useContext, useState, ReactNode } from 'react';
import http, { setAuthTokens, clearAuthTokens } from '../lib/http';
import { useToast } from '../lib/toast';

export type Role = 'admin' | 'office' | 'supervisor' | 'promoter';

interface User {
  username: string;
  role: Role;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  login: async () => {
    throw new Error('AuthProvider not ready');
  },
  logout: () => {
    throw new Error('AuthProvider not ready');
  },
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });
  const toast = useToast();

  const login = async (username: string, password: string) => {
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);
    try {
      const { data } = await http.post('/auth/login', body);
      setAuthTokens(data.access_token, data.refresh_token);
      localStorage.setItem('accessToken', data.access_token);
      localStorage.setItem('refreshToken', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      setUser(data.user);
    } catch (e: any) {
      toast(e.message || 'Не удалось войти', 'error');
      throw e;
    }
  };

  const logout = () => {
    clearAuthTokens();
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
