import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import ErrorBoundary from './components/ErrorBoundary'
import RequireAuth from './components/RequireAuth'
import RequireRole from './components/RequireRole'
import Layout from './components/Layout'

import LoginPage from './pages/Login'
import Dashboard from './pages/Dashboard'
import InvitesPage from './pages/Invites'
import InviteRegisterPage from './pages/InviteRegister'
import { getApiBase } from './shared/http'

// Создаём роутер как раньше…
const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/register/:code', element: <InviteRegisterPage /> },
  {
    path: '/',
    element: (
      <RequireAuth>
        <Layout><Dashboard /></Layout>
      </RequireAuth>
    ),
  },
  {
    path: '/invites',
    element: (
      <RequireAuth>
        <RequireRole roles={['admin', 'office']}>
          <Layout><InvitesPage /></Layout>
        </RequireRole>
      </RequireAuth>
    ),
  },
])

// Полезный лог — сразу видно, какой base URL реально используется
console.info('[HTTP] API base =', getApiBase())

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <RouterProvider router={router} />
    </ErrorBoundary>
  </React.StrictMode>
)
