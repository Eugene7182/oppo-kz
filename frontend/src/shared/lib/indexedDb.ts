/**
 * Простая обёртка над IndexedDB для офлайн-режима.
 * Храним локальные продажи и outbox запросов.
 */
export type StoreNames = "sales" | "plans" | "outbox";

const DB_NAME = "oppo-kz-app";
const DB_VERSION = 1;

export type OutboxRecord = {
  id: string;
  endpoint: string;
  payload: unknown;
  createdAt: number;
  status: "pending" | "synced" | "failed";
  retries: number;
};

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains("sales")) {
        db.createObjectStore("sales", { keyPath: "id" });
      }
      if (!db.objectStoreNames.contains("plans")) {
        db.createObjectStore("plans", { keyPath: "id" });
      }
      if (!db.objectStoreNames.contains("outbox")) {
        const store = db.createObjectStore("outbox", { keyPath: "id" });
        store.createIndex("status", "status", { unique: false });
      }
    };

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

async function withStore<T>(
  storeName: StoreNames,
  mode: IDBTransactionMode,
  callback: (store: IDBObjectStore) => T | Promise<T>,
): Promise<T> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, mode);
    const store = tx.objectStore(storeName);

    Promise.resolve(callback(store))
      .then(resolve)
      .catch(reject);

    tx.oncomplete = () => db.close();
    tx.onerror = () => reject(tx.error);
  });
}

export async function upsertRecord<T extends { id: string }>(store: StoreNames, value: T) {
  return withStore(store, "readwrite", (storeInstance) => {
    storeInstance.put(value);
  });
}

export async function bulkUpsert<T extends { id: string }>(store: StoreNames, values: T[]) {
  return withStore(store, "readwrite", (storeInstance) => {
    values.forEach((value) => storeInstance.put(value));
  });
}

export async function readAll<T>(store: StoreNames): Promise<T[]> {
  return withStore(store, "readonly", (storeInstance) => {
    return new Promise<T[]>((resolve, reject) => {
      const request = storeInstance.getAll();
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result as T[]);
    });
  });
}

export async function removeRecord(store: StoreNames, id: string) {
  return withStore(store, "readwrite", (storeInstance) => {
    storeInstance.delete(id);
  });
}

export async function addOutboxRecord(record: OutboxRecord) {
  return upsertRecord("outbox", record);
}

export async function readPendingOutbox(): Promise<OutboxRecord[]> {
  return withStore("outbox", "readonly", (storeInstance) => {
    return new Promise<OutboxRecord[]>((resolve, reject) => {
      const index = storeInstance.index("status");
      const request = index.getAll("pending");
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result as OutboxRecord[]);
    });
  });
}

export async function updateOutboxStatus(id: string, status: OutboxRecord["status"], retries?: number) {
  return withStore("outbox", "readwrite", (storeInstance) => {
    const request = storeInstance.get(id);
    request.onsuccess = () => {
      const current = request.result as OutboxRecord | undefined;
      if (!current) return;
      storeInstance.put({ ...current, status, retries: retries ?? current.retries });
    };
  });
}

export async function clearStore(store: StoreNames) {
  return withStore(store, "readwrite", (storeInstance) => storeInstance.clear());
}
