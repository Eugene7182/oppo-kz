
import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import ErrorBoundary from './components/ErrorBoundary'
import RequireAuth from './components/RequireAuth'
import RequireRole from './components/RequireRole'
import Layout from './components/Layout'

import LoginPage from './pages/Login'
import Dashboard from './pages/Dashboard'
import InviteRegisterPage from './pages/InviteRegister'
import InvitesPage from './pages/Invites'
import SalesPage from './features/sales/SalesPage'
import PriceListPage from './features/price-list/PriceListPage'
import StoresPage from './pages/Stores'
import SkuPage from './pages/Sku'
import ReconciliationPage from './pages/Reconciliation'
import StoreCoefficientsPage from './pages/StoreCoefficients'
import BonusGridsPage from './pages/BonusGrids'
import ImportsPage from './pages/Imports'
import StockMovesPage from './pages/StockMoves'
import InventoryPage from './pages/Inventory'
import { initSentry } from './sentry'

initSentry()

const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/register/:code', element: <InviteRegisterPage /> },
  { path: '/', element: <RequireAuth><Layout><Dashboard/></Layout></RequireAuth> },
  { path: '/invites', element: <RequireAuth><RequireRole roles={['admin','office']}><Layout><InvitesPage/></Layout></RequireRole></RequireAuth> },
  { path: '/sales', element: <RequireAuth><Layout><SalesPage/></Layout></RequireAuth> },
  { path: '/price-list', element: <RequireAuth><Layout><PriceListPage/></Layout></RequireAuth> },
  { path: '/stores', element: <RequireAuth><Layout><StoresPage/></Layout></RequireAuth> },
  { path: '/sku', element: <RequireAuth><Layout><SkuPage/></Layout></RequireAuth> },
  { path: '/coeffs', element: <RequireAuth><Layout><StoreCoefficientsPage/></Layout></RequireAuth> },
  { path: '/bonus', element: <RequireAuth><RequireRole roles={['admin','office']}><Layout><BonusGridsPage/></Layout></RequireRole></RequireAuth> },
  { path: '/imports', element: <RequireAuth><RequireRole roles={['admin','office']}><Layout><ImportsPage/></Layout></RequireRole></RequireAuth> },
  { path: '/moves', element: <RequireAuth><RequireRole roles={['admin','office','supervisor']}><Layout><StockMovesPage/></Layout></RequireRole></RequireAuth> },
  { path: '/inventory', element: <RequireAuth><RequireRole roles={['admin','office','supervisor']}><Layout><InventoryPage/></Layout></RequireRole></RequireAuth> },
  { path: '/reconciliation', element: <RequireAuth><Layout><ReconciliationPage/></Layout></RequireAuth> },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary><RouterProvider router={router} /></ErrorBoundary>
  </React.StrictMode>
)
