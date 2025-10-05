const CACHE_NAME = "oppo-shell-v1";
const SHELL_ASSETS = [
  "./",
  "./index.html",
  "./style.css",
  "./script.js",
  "./images/oppo-logo.svg",
  "./images/oppo-logo@2x.svg",
];
const DB_NAME = "oppo-dashboard";
const DB_VERSION = 1;
const STORE_NAMES = {
  outbox: "outbox",
  sales: "sales",
  plans: "plans",
  reference: "reference",
  meta: "meta",
};
const QUEUE_BATCH_SIZE = 5;
const MAX_RETRIES = 5;
const RETRY_BASE_DELAY = 2000;

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS)).catch(() => undefined)
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  const method = request.method.toUpperCase();
  if (method === "GET") {
    event.respondWith(handleGetRequest(request));
    return;
  }
  const url = new URL(request.url);
  const offlineType = request.headers.get("X-Offline-Type");
  const isMutation = ["POST", "PUT", "DELETE"].includes(method);
  const isSameOrigin = url.origin === self.location.origin;
  const isApiRequest = offlineType || isSameOrigin || url.pathname.includes("/api/");
  if (isMutation && isApiRequest) {
    event.respondWith(handleMutatingRequest(request, offlineType));
  }
});

self.addEventListener("sync", (event) => {
  if (event.tag === "oppo-sync") {
    event.waitUntil(handleBackgroundSync());
  }
});

async function handleBackgroundSync() {
  await notifyClients("sync:trigger");
  await flushOutbox();
}

async function handleGetRequest(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  if (cached) {
    fetch(request)
      .then((response) => {
        if (response && response.ok) {
          cache.put(request, response.clone());
        }
      })
      .catch(() => undefined);
    return cached;
  }
  try {
    const response = await fetch(request);
    if (response && response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    return cached || Response.error();
  }
}

async function handleMutatingRequest(request, offlineType) {
  try {
    const response = await fetch(request.clone());
    if (!response || !response.ok) {
      await enqueueRequest(request, offlineType, response);
      return buildQueuedResponse();
    }
    return response;
  } catch (error) {
    await enqueueRequest(request, offlineType, null, error);
    return buildQueuedResponse();
  }
}

function buildQueuedResponse() {
  return new Response(JSON.stringify({ queued: true }), {
    status: 202,
    headers: { "Content-Type": "application/json" },
  });
}

async function enqueueRequest(request, offlineType, response, networkError) {
  const body = await readRequestBody(request);
  const safeHeaders = sanitizeHeaders(request.headers);
  const headerObject = Object.fromEntries(safeHeaders.entries());
  const type = offlineType || headerObject["X-Offline-Type"] || "generic.mutation";
  const idempotencyKey =
    headerObject["Idempotency-Key"] ||
    (body && typeof body === "object" && body?.id) ||
    (self.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`);
  headerObject["Idempotency-Key"] = idempotencyKey;
  const record = {
    type,
    payload: {
      url: request.url,
      method: request.method,
      body,
      headers: headerObject,
      collection: headerObject["X-Offline-Collection"] || null,
      localId: headerObject["X-Offline-Id"] || null,
      idempotencyKey,
    },
    lastError: networkError?.message || response?.statusText || "Network unavailable",
  };
  await addToOutbox(record);
  await ensureBackgroundSync();
  await notifyClients("outbox:queued", {
    id: idempotencyKey,
    collection: record.payload.collection,
    localId: record.payload.localId,
  });
  await notifyClients("sync:trigger");
}

function readRequestBody(request) {
  if (request.method === "GET" || request.method === "HEAD") {
    return Promise.resolve(null);
  }
  return request
    .clone()
    .text()
    .then((text) => {
      if (!text) return null;
      try {
        return JSON.parse(text);
      } catch (error) {
        return text;
      }
    })
    .catch(() => null);
}

function sanitizeHeaders(headers) {
  const safe = new Headers();
  const allowed = [
    "Content-Type",
    "Accept",
    "X-Offline-Type",
    "X-Offline-Collection",
    "X-Offline-Id",
    "Idempotency-Key",
  ];
  headers.forEach((value, key) => {
    if (allowed.includes(key)) {
      safe.set(key, value);
    }
  });
  return safe;
}

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAMES.outbox)) {
        const outbox = db.createObjectStore(STORE_NAMES.outbox, { keyPath: "id" });
        outbox.createIndex("status", "status", { unique: false });
        outbox.createIndex("nextAttempt", "nextAttempt", { unique: false });
      }
      if (!db.objectStoreNames.contains(STORE_NAMES.sales)) {
        db.createObjectStore(STORE_NAMES.sales, { keyPath: "id" });
      }
      if (!db.objectStoreNames.contains(STORE_NAMES.plans)) {
        db.createObjectStore(STORE_NAMES.plans, { keyPath: "id" });
      }
      if (!db.objectStoreNames.contains(STORE_NAMES.reference)) {
        db.createObjectStore(STORE_NAMES.reference, { keyPath: "key" });
      }
      if (!db.objectStoreNames.contains(STORE_NAMES.meta)) {
        db.createObjectStore(STORE_NAMES.meta, { keyPath: "key" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function addToOutbox(entry) {
  const db = await openDatabase();
  const tx = db.transaction(STORE_NAMES.outbox, "readwrite");
  const store = tx.objectStore(STORE_NAMES.outbox);
  const now = Date.now();
  const recordId = entry.payload.idempotencyKey || (self.crypto?.randomUUID?.() || `${now}-${Math.random()}`);
  const payload = {
    ...entry.payload,
    idempotencyKey: entry.payload.idempotencyKey || recordId,
  };
  const record = {
    id: recordId,
    type: entry.type,
    payload,
    created_at: new Date(now).toISOString(),
    status: "queued",
    retries: entry.retries ?? 0,
    nextAttempt: now,
    lastError: entry.lastError || null,
  };
  store.put(record);
  return new Promise((resolve, reject) => {
    tx.oncomplete = resolve;
    tx.onabort = tx.onerror = () => reject(tx.error);
  });
}

async function flushOutbox() {
  const db = await openDatabase();
  let batch = await getReadyOutboxBatch(db, QUEUE_BATCH_SIZE);
  if (!batch.length) {
    return;
  }
  let processed = false;
  while (batch.length) {
    processed = true;
    for (const record of batch) {
      await processOutboxRecord(db, record);
    }
    batch = await getReadyOutboxBatch(db, QUEUE_BATCH_SIZE);
  }
  if (processed) {
    await notifyClients("sync:complete");
  }
}

function getReadyOutboxBatch(db, limit) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAMES.outbox, "readonly");
    const store = tx.objectStore(STORE_NAMES.outbox);
    const index = store.index("nextAttempt");
    const records = [];
    const request = index.openCursor(IDBKeyRange.upperBound(Date.now()));
    request.onsuccess = (event) => {
      const cursor = event.target.result;
      if (!cursor || records.length >= limit) {
        resolve(records);
        return;
      }
      const value = cursor.value;
      if (value.status === "queued") {
        records.push(value);
      }
      cursor.continue();
    };
    request.onerror = () => reject(request.error);
    tx.onabort = () => reject(tx.error);
  });
}

async function processOutboxRecord(db, record) {
  const headers = new Headers(record.payload.headers || {});
  const idempotencyKey = record.payload.idempotencyKey || record.id;
  headers.set("Idempotency-Key", idempotencyKey);
  const rawBody = record.payload.body;
  const body =
    rawBody === undefined || rawBody === null
      ? undefined
      : typeof rawBody === "string"
      ? rawBody
      : JSON.stringify(rawBody);

  await putOutboxRecord(db, { ...record, status: "sending", nextAttempt: Date.now() });

  try {
    const response = await fetch(record.payload.url, {
      method: record.payload.method,
      headers,
      body,
      credentials: "include",
    });
    if (response.status === 409) {
      let serverPayload = null;
      try {
        serverPayload = await response.clone().json();
      } catch (error) {
        serverPayload = null;
      }
      const conflictRecord = {
        ...record,
        status: "conflict",
        retries: record.retries || 0,
        nextAttempt: null,
        lastError: "409 Conflict",
        conflictPayload: serverPayload,
      };
      await putOutboxRecord(db, conflictRecord);
      await updateLocalRecordStatus(db, record.payload.collection, record.payload.localId, "conflict", {
        lastError: "Конфликт данных",
        serverSnapshot: serverPayload,
      });
      await notifyClients("outbox:failed", {
        id: record.id,
        message: "Конфликт данных",
        status: "conflict",
      });
      return;
    }
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const sentRecord = {
      ...record,
      status: "sent",
      retries: 0,
      nextAttempt: null,
      lastError: null,
    };
    await putOutboxRecord(db, sentRecord);
    await updateLocalRecordStatus(db, record.payload.collection, record.payload.localId, "sent", {
      updatedAt: new Date().toISOString(),
    });
    await notifyClients("outbox:sent", { id: record.id });
  } catch (error) {
    const retries = (record.retries || 0) + 1;
    if (retries >= MAX_RETRIES) {
      const failedRecord = {
        ...record,
        status: "failed",
        retries,
        nextAttempt: null,
        lastError: error.message,
      };
      await putOutboxRecord(db, failedRecord);
      await updateLocalRecordStatus(db, record.payload.collection, record.payload.localId, "failed", {
        lastError: error.message,
      });
      await notifyClients("outbox:failed", {
        id: record.id,
        message: error.message,
        status: "failed",
      });
    } else {
      const delay = Math.min(RETRY_BASE_DELAY * Math.pow(2, retries - 1), 5 * 60 * 1000);
      const retryRecord = {
        ...record,
        status: "queued",
        retries,
        nextAttempt: Date.now() + delay,
        lastError: error.message,
      };
      await putOutboxRecord(db, retryRecord);
      await updateLocalRecordStatus(db, record.payload.collection, record.payload.localId, "queued", {
        lastError: error.message,
      });
      await ensureBackgroundSync();
    }
  }
}

function putOutboxRecord(db, record) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAMES.outbox, "readwrite");
    const store = tx.objectStore(STORE_NAMES.outbox);
    store.put(record);
    tx.oncomplete = resolve;
    tx.onabort = tx.onerror = () => reject(tx.error);
  });
}

function updateLocalRecordStatus(db, collectionKey, id, status, details = {}) {
  if (!collectionKey || !id) {
    return Promise.resolve();
  }
  const storeName = STORE_NAMES[collectionKey];
  if (!storeName) {
    return Promise.resolve();
  }
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, "readwrite");
    const store = tx.objectStore(storeName);
    const request = store.get(id);
    request.onsuccess = () => {
      const entity = request.result;
      if (!entity) {
        return;
      }
      const next = {
        ...entity,
        syncStatus: status,
        lastError: details.lastError ?? entity.lastError ?? null,
        conflict: status === "conflict",
      };
      if (details.serverSnapshot !== undefined) {
        next.serverSnapshot = details.serverSnapshot;
      }
      if (details.updatedAt) {
        next.updatedAt = details.updatedAt;
      } else if (status === "sent") {
        next.updatedAt = new Date().toISOString();
      }
      store.put(next);
    };
    request.onerror = () => reject(request.error);
    tx.oncomplete = () => resolve();
    tx.onabort = tx.onerror = () => reject(tx.error);
  });
}

async function notifyClients(type, payload) {
  const clientsList = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
  clientsList.forEach((client) => client.postMessage({ type, payload }));
}

async function ensureBackgroundSync() {
  if (!self.registration?.sync) {
    return;
  }
  try {
    await self.registration.sync.register("oppo-sync");
  } catch (error) {
    console.warn("Background sync registration failed", error);
  }
}
