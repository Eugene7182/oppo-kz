import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import RequireAuth from './components/RequireAuth';
import RequireRole from './components/RequireRole';
import Layout from './components/Layout';

import LoginPage from './pages/Login';
import Dashboard from './pages/Dashboard';
import InvitesPage from './pages/Invites';

const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },

  {
    path: '/',
    element: (
      <RequireAuth>
        <Layout>
          <Dashboard />
        </Layout>
      </RequireAuth>
    ),
  },

  {
    path: '/invites',
    element: (
      <RequireAuth>
        <RequireRole roles={['admin', 'office']}>
          <Layout>
            <InvitesPage />
          </Layout>
        </RequireRole>
      </RequireAuth>
    ),
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
