import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface NavItem {
  to: string;
  label: string;
  roles?: string[];
}

// Define navigation items with role restrictions
const navItems: NavItem[] = [
  { to: '/', label: 'Health' },
  { to: '/dicts/networks', label: 'Networks', roles: ['admin', 'office'] },
  { to: '/dicts/stores', label: 'Stores', roles: ['admin', 'office'] },
  { to: '/price/upload', label: 'Price Upload', roles: ['admin'] },
  { to: '/price/sku', label: 'SKU List', roles: ['admin'] },
  { to: '/imports/jobs', label: 'Jobs', roles: ['admin'] },
  { to: '/inventory/balances', label: 'Balances', roles: ['admin', 'office', 'supervisor'] },
  { to: '/inventory/adjust', label: 'Adjust', roles: ['admin', 'office'] },
  { to: '/moves', label: 'Moves', roles: ['admin', 'office'] },
  { to: '/moves/create', label: 'Create Move', roles: ['admin', 'office'] },
  { to: '/sales/network', label: 'Network Sales', roles: ['admin', 'office'] },
  { to: '/sales/promoter', label: 'Promoter Sales', roles: ['admin', 'office', 'supervisor', 'promoter'] },
  { to: '/sales/reconcile', label: 'Reconcile', roles: ['admin'] },
  { to: '/logistics/shipments', label: 'Shipments', roles: ['admin', 'office'] },
  { to: '/logistics/in-transit', label: 'In Transit', roles: ['admin', 'office'] },
  { to: '/messages', label: 'Messages', roles: ['admin', 'office'] },
  { to: '/messages/create', label: 'Create Message', roles: ['admin', 'office'] },
  { to: '/flags', label: 'Flags', roles: ['admin'] },
];

// Layout with top navigation and outlet
export default function Layout() {
  const { me, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-blue-600 text-white px-4 py-2 flex gap-4 items-center">
        <span className="font-bold">Demo</span>
        {navItems
          .filter((i) => !i.roles || (me && i.roles.includes(me.role)))
          .map((i) => (
            <NavLink key={i.to} to={i.to} className="hover:underline">
              {i.label}
            </NavLink>
          ))}
        <div className="flex-1" />
        {me && (
          <button onClick={logout} className="underline">
            Logout
          </button>
        )}
      </nav>
      <main className="p-4 flex-1">
        <Outlet />
      </main>
    </div>
  );
}
