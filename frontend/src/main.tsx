import InviteRegisterPage from './pages/InviteRegister'

// ...
const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/register/:code', element: <InviteRegisterPage /> },  // ← добавили

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
])
