import { Navigate, Route, Routes } from "react-router-dom";
import { useMemo } from "react";

import { useAuth } from "../providers/AuthProvider";
import { AppLayout } from "./AppLayout";
import { PromoterHomePage } from "../../pages/promoter/home";
import { SupervisorRegionPage } from "../../pages/supervisor/region";
import { OfficeAnalyticsPage } from "../../pages/office/analytics";
import { AdminUsersPage } from "../../pages/admin/users";
import { AdminInvitesPage } from "../../pages/admin/invites";
import { AdminDictionariesPage } from "../../pages/admin/dictionaries";
import { AdminBonusSchemesPage } from "../../pages/admin/bonus-schemes";
import { LoginByRole } from "../../pages/login";

const DEFAULT_ROUTES: Record<string, string> = {
  promoter: "/promoter/home",
  supervisor: "/supervisor/region",
  office: "/office/analytics",
  admin: "/admin/users",
};

export function AppRoutes() {
  const { user, role } = useAuth();

  const defaultPath = useMemo(() => {
    if (!role) return "/login";
    return DEFAULT_ROUTES[role];
  }, [role]);

  if (!user) {
    return <LoginByRole />;
  }

  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to={defaultPath} replace />} />
        <Route path="/promoter/home" element={<PromoterHomePage />} />
        <Route path="/supervisor/region" element={<SupervisorRegionPage />} />
        <Route path="/office/analytics" element={<OfficeAnalyticsPage />} />
        <Route path="/admin/users" element={<AdminUsersPage />} />
        <Route path="/admin/invites" element={<AdminInvitesPage />} />
        <Route path="/admin/dictionaries" element={<AdminDictionariesPage />} />
        <Route path="/admin/bonus-schemes" element={<AdminBonusSchemesPage />} />
      </Route>
      <Route path="*" element={<Navigate to={defaultPath} replace />} />
    </Routes>
  );
}
