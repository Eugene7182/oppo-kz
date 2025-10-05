import { NavLink, Outlet } from "react-router-dom";
import { Menu, LogOut, RefreshCw } from "lucide-react";
import { useMemo, useState } from "react";

import { useAuth } from "../providers/AuthProvider";
import { useOffline } from "../providers/OfflineProvider";
import { StatusBanner } from "../../widgets/StatusBanner";
import { SyncControl } from "../../features/sync-control";

export function AppLayout() {
  const { user, logout } = useAuth();
  const { status, queueSize } = useOffline();
  const [open, setOpen] = useState(false);

  const links = useMemo(() => {
    switch (user?.role) {
      case "promoter":
        return [{ to: "/promoter/home", label: "Мои продажи" }];
      case "supervisor":
        return [{ to: "/supervisor/region", label: "Регион" }];
      case "office":
        return [{ to: "/office/analytics", label: "Аналитика" }];
      case "admin":
        return [
          { to: "/admin/users", label: "Пользователи" },
          { to: "/admin/invites", label: "Инвайты" },
          { to: "/admin/dictionaries", label: "Справочники" },
          { to: "/admin/bonus-schemes", label: "Бонусы" },
        ];
      default:
        return [];
    }
  }, [user?.role]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-3">
          <button
            className="rounded-lg border border-slate-200 p-2 text-slate-700 lg:hidden"
            onClick={() => setOpen((prev) => !prev)}
            aria-label="Toggle navigation"
          >
            <Menu size={18} />
          </button>
          <div className="font-semibold uppercase tracking-wide text-slate-700">OPPO KZ</div>
          <div className="ml-auto flex items-center gap-3 text-sm text-slate-600">
            <span>{user?.fullName}</span>
            <span className="rounded-full bg-slate-100 px-2 py-1 text-xs uppercase">{user?.role}</span>
            <button
              onClick={logout}
              className="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
            >
              <LogOut size={14} /> Выйти
            </button>
          </div>
        </div>
        <nav className={`border-t border-slate-200 bg-white lg:border-none ${open ? "block" : "hidden lg:block"}`}>
          <div className="mx-auto flex max-w-6xl flex-col gap-1 px-4 py-3 lg:flex-row lg:items-center lg:gap-4">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-medium transition hover:bg-slate-100 ${
                    isActive ? "bg-slate-900 text-white" : "text-slate-600"
                  }`
                }
                onClick={() => setOpen(false)}
              >
                {link.label}
              </NavLink>
            ))}
            <div className="lg:ml-auto">
              <SyncControl variant="inline" />
            </div>
          </div>
        </nav>
        <StatusBanner status={status} queueSize={queueSize} />
      </header>

      <main className="mx-auto flex max-w-6xl flex-1 flex-col gap-6 px-4 py-6">
        <Outlet />
      </main>

      <footer className="mt-12 border-t border-slate-200 bg-white/80 py-6 text-center text-xs text-slate-500">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4">
          <span>© {new Date().getFullYear()} OPPO Kazakhstan</span>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-500 hover:bg-slate-100"
          >
            <RefreshCw size={14} /> Перезагрузить
          </button>
        </div>
      </footer>
    </div>
  );
}
