import { BrowserRouter } from "react-router-dom";
import type { ReactNode } from "react";

import { AuthProvider } from "./AuthProvider";
import { OfflineProvider } from "./OfflineProvider";

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <BrowserRouter>
      <AuthProvider>
        <OfflineProvider>{children}</OfflineProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
