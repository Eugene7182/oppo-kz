import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { api } from "../../shared/api/http";
import { readPendingOutbox, updateOutboxStatus, OutboxRecord } from "../../shared/lib/indexedDb";
import { useNetworkStatus } from "../../shared/hooks/useNetworkStatus";

type SyncStatus = "online" | "offline" | "queued" | "syncing";

type OfflineContextValue = {
  status: SyncStatus;
  queueSize: number;
  pending: OutboxRecord[];
  lastSyncAt: number | null;
  syncNow: () => Promise<void>;
};

const OfflineContext = createContext<OfflineContextValue | undefined>(undefined);

export function OfflineProvider({ children }: { children: ReactNode }) {
  const network = useNetworkStatus();
  const [pending, setPending] = useState<OutboxRecord[]>([]);
  const [lastSyncAt, setLastSyncAt] = useState<number | null>(null);
  const [syncing, setSyncing] = useState(false);

  const refreshPending = useCallback(async () => {
    const items = await readPendingOutbox();
    setPending(items);
  }, []);

  useEffect(() => {
    refreshPending();
  }, [refreshPending]);

  const syncNow = useCallback(async () => {
    setSyncing(true);
    try {
      if (pending.length === 0) {
        await api.sync.pull();
        setLastSyncAt(Date.now());
        return;
      }
      for (const record of pending) {
        try {
          await api.sync.push();
          await updateOutboxStatus(record.id, "synced", record.retries + 1);
        } catch (error) {
          await updateOutboxStatus(record.id, "failed", record.retries + 1);
          console.error("[sync] failed", error);
        }
      }
      setLastSyncAt(Date.now());
    } finally {
      setSyncing(false);
      refreshPending();
    }
  }, [pending, refreshPending]);

  useEffect(() => {
    if (network === "online" && pending.length > 0 && !syncing) {
      void syncNow();
    }
  }, [network, pending.length, syncNow, syncing]);

  const status: SyncStatus = useMemo(() => {
    if (syncing) return "syncing";
    if (network === "offline") return "offline";
    if (pending.length > 0) return "queued";
    return "online";
  }, [network, pending.length, syncing]);

  const value = useMemo(
    () => ({
      status,
      queueSize: pending.length,
      pending,
      lastSyncAt,
      syncNow,
    }),
    [status, pending, lastSyncAt, syncNow],
  );

  return <OfflineContext.Provider value={value}>{children}</OfflineContext.Provider>;
}

export function useOffline() {
  const ctx = useContext(OfflineContext);
  if (!ctx) throw new Error("useOffline must be used within OfflineProvider");
  return ctx;
}
