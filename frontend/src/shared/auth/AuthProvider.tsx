// frontend/src/shared/auth/AuthProvider.tsx
import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import * as auth from "../api/auth";

type User = {
  id: number;
  username: string;
  role: "super" | "promoter";
  full_name?: string | null;
};

type Ctx = {
  user: User | null;
  loading: boolean;
  login: (u: string, p: string) => Promise<void>;
  logout: () => void;
  reload: () => Promise<void>;
};

const AuthCtx = createContext<Ctx>({
  user: null,
  loading: true,
  async login() {},
  logout() {},
  async reload() {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function reload() {
    try {
      const me = await auth.me();
      setUser(me as any);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // если есть токен — подтянем профиль
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(u: string, p: string) {
    await auth.login(u, p);
    await reload();
  }

  function logout() {
    auth.logout();
    setUser(null);
  }

  return (
    <AuthCtx.Provider value={{ user, loading, login, logout, reload }}>
      {children}
    </AuthCtx.Provider>
  );
}

export function useAuth() {
  return useContext(AuthCtx);
}
