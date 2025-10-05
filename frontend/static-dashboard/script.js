/**
 * Responsive dashboard prototype for OPPO KZ.
 * Offline-first extension with IndexedDB, outbox and background sync.
 */

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
const SEED_VERSION = "2024-04-15";
const API_BASE =
  (window.APP_CONFIG && window.APP_CONFIG.apiBase) ||
  document.documentElement.dataset.apiBase ||
  "";
const SERVICE_WORKER_PATH = "./sw.js";

const syncStatusLabels = {
  queued: "В очереди",
  sending: "Отправка",
  sent: "Синхронизировано",
  failed: "Ошибка",
  conflict: "Конфликт",
};

const syncStatusPriority = {
  conflict: 5,
  failed: 4,
  queued: 3,
  sending: 2,
  sent: 1,
};

const accountStatusLabels = {
  active: "Активен",
  pending: "Ожидает",
};

const monthNames = [
  "Январь",
  "Февраль",
  "Март",
  "Апрель",
  "Май",
  "Июнь",
  "Июль",
  "Август",
  "Сентябрь",
  "Октябрь",
  "Ноябрь",
  "Декабрь",
];

const offlineDataCache = {
  sales: [],
  plans: [],
  users: [],
  training: [],
};

let dbPromise = null;

const seedSales = [
  {
    id: "sale-2024-04-01-promoter",
    store: "Mega Alma",
    office: "HQ",
    supervisor: "Юг",
    source: "promoter",
    channel: "promoter",
    month: "2024-04",
    date: "2024-04-01",
    amount: 1820000,
    quantity: 36,
    syncStatus: "sent",
    updatedAt: "2024-04-10T05:10:00Z",
  },
  {
    id: "sale-2024-04-02-retail",
    store: "Sulpak Esentai",
    office: "HQ",
    supervisor: "Юг",
    source: "retail",
    channel: "retail",
    month: "2024-04",
    date: "2024-04-02",
    amount: 1460000,
    quantity: 28,
    syncStatus: "sent",
    updatedAt: "2024-04-10T05:12:00Z",
  },
  {
    id: "sale-2024-04-03-promoter",
    store: "Mechta Dostyk",
    office: "HQ",
    supervisor: "Юг",
    source: "promoter",
    channel: "promoter",
    month: "2024-04",
    date: "2024-04-03",
    amount: 1310000,
    quantity: 24,
    syncStatus: "sent",
    updatedAt: "2024-04-10T05:14:00Z",
  },
  {
    id: "sale-2024-04-04-promoter",
    store: "Mega Alma",
    office: "HQ",
    supervisor: "Юг",
    source: "promoter",
    channel: "promoter",
    month: "2024-04",
    date: "2024-04-04",
    amount: 1980000,
    quantity: 39,
    syncStatus: "queued",
    updatedAt: "2024-04-12T07:20:00Z",
  },
  {
    id: "sale-2024-03-28-promoter",
    store: "Mega Alma",
    office: "HQ",
    supervisor: "Юг",
    source: "promoter",
    channel: "promoter",
    month: "2024-03",
    date: "2024-03-28",
    amount: 1580000,
    quantity: 30,
    syncStatus: "sent",
    updatedAt: "2024-03-30T04:30:00Z",
  },
  {
    id: "sale-2024-04-05-retail",
    store: "Technodom Turkistan",
    office: "Регион Юг",
    supervisor: "Юг",
    source: "retail",
    channel: "retail",
    month: "2024-04",
    date: "2024-04-05",
    amount: 990000,
    quantity: 18,
    syncStatus: "sent",
    updatedAt: "2024-04-10T05:18:00Z",
  },
];

const seedPlans = [
  {
    id: "plan-2024-04-mega-alma",
    store: "Mega Alma",
    office: "HQ",
    supervisor: "Юг",
    promoterId: "promoter-001",
    promoter: "Нурия Бахыт",
    month: "2024-04",
    plan: 420000,
    fact: 480000,
    bonus: 65000,
    syncStatus: "sent",
    updatedAt: "2024-04-10T08:30:00Z",
    conflict: false,
  },
  {
    id: "plan-2024-04-sulpak-esentai",
    store: "Sulpak Esentai",
    office: "HQ",
    supervisor: "Юг",
    promoterId: "promoter-002",
    promoter: "Еламан Кайрат",
    month: "2024-04",
    plan: 380000,
    fact: 322000,
    bonus: 28000,
    syncStatus: "queued",
    updatedAt: "2024-04-12T06:20:00Z",
    conflict: false,
    localOnly: true,
  },
  {
    id: "plan-2024-04-mechta-dostyk",
    store: "Mechta Dostyk",
    office: "HQ",
    supervisor: "Юг",
    promoterId: "promoter-003",
    promoter: "Айдана Сеит",
    month: "2024-04",
    plan: 300000,
    fact: 280000,
    bonus: 24000,
    syncStatus: "failed",
    updatedAt: "2024-04-09T11:10:00Z",
    conflict: false,
    lastError: "HTTP 500",
  },
  {
    id: "plan-2024-03-mega-alma",
    store: "Mega Alma",
    office: "HQ",
    supervisor: "Юг",
    promoterId: "promoter-001",
    promoter: "Нурия Бахыт",
    month: "2024-03",
    plan: 400000,
    fact: 390000,
    bonus: 58000,
    syncStatus: "conflict",
    updatedAt: "2024-04-05T10:00:00Z",
    conflict: true,
    serverSnapshot: {
      plan: 430000,
      fact: 410000,
      bonus: 60000,
      updatedAt: "2024-04-04T07:00:00Z",
    },
  },
];

const seedUsers = [
  {
    id: "user-001",
    name: "Мария Токтарова",
    role: "office",
    region: "HQ",
    lastLogin: "2024-04-10T09:22:00+06:00",
    accountStatus: "active",
    syncStatus: "sent",
  },
  {
    id: "user-002",
    name: "Ержан Абдрахман",
    role: "supervisor",
    region: "Юг",
    lastLogin: "2024-04-10T08:14:00+06:00",
    accountStatus: "active",
    syncStatus: "sent",
  },
  {
    id: "user-003",
    name: "Нурия Бахыт",
    role: "promoter",
    region: "Алматы",
    lastLogin: "2024-04-09T18:33:00+06:00",
    accountStatus: "pending",
    syncStatus: "queued",
  },
  {
    id: "user-004",
    name: "Адиль Серик",
    role: "admin",
    region: "HQ",
    lastLogin: "2024-04-08T11:08:00+06:00",
    accountStatus: "active",
    syncStatus: "sent",
  },
  {
    id: "user-005",
    name: "Айгерим Иса",
    role: "admin",
    region: "HQ",
    lastLogin: "2024-04-10T10:40:00+06:00",
    accountStatus: "active",
    syncStatus: "failed",
    lastError: "401 Unauthorized",
  },
];

const seedTraining = [
  {
    date: "12.04.2024",
    city: "Алматы",
    topic: "Reno10 камера",
    attendees: "16",
    status: "Запланировано",
  },
  {
    date: "18.04.2024",
    city: "Астана",
    topic: "Финальный апсейл",
    attendees: "18",
    status: "Подтверждено",
  },
  {
    date: "22.04.2024",
    city: "Шымкент",
    topic: "Find X5 премиум",
    attendees: "12",
    status: "Формируется",
  },
];

const offlineMetaSeed = {
  watermark: "2024-04-10T12:00:00Z",
};

const state = {
  currentRole: "admin",
  chart: {
    grain: "day",
    secondaryAxis: false,
  },
  filters: {
    office: {
      scope: ["Все"],
      period: ["Текущий месяц"],
      timeGrain: ["День"],
      models: ["Reno10", "Find X5"],
      metric: ["Шт."],
      compare: ["WoW"],
      lfl: ["LFL выкл"],
    },
    supervisor: {
      scope: ["Юг"],
      period: ["Текущая неделя"],
      timeGrain: ["Неделя"],
      models: ["Reno10"],
      metric: ["₸"],
      compare: ["WoW"],
      lfl: ["LFL вкл"],
    },
  },
};

const filtersConfig = {
  office: [
    { key: "scope", label: "Охват", multi: false, options: ["Все", "Сеть", "Магазин"] },
    {
      key: "period",
      label: "Период",
      multi: false,
      options: ["Текущая неделя", "Текущий месяц", "Этот квартал", "Произвольный"],
    },
    { key: "timeGrain", label: "Гранулярность", multi: false, options: ["День", "Неделя", "Месяц", "Год"] },
    {
      key: "models",
      label: "Модели",
      multi: true,
      options: ["Reno10", "Find X5", "A78", "A17", "Find N3"],
    },
    { key: "metric", label: "Метрика", multi: false, options: ["Шт.", "₸", "Achv%", "Bonus"] },
    { key: "compare", label: "Сравнение", multi: true, options: ["WoW", "MoM", "YoY"] },
    { key: "lfl", label: "LFL", multi: false, options: ["LFL вкл", "LFL выкл"] },
  ],
  supervisor: [
    { key: "scope", label: "Регион", multi: false, options: ["Юг", "Центр"] },
    { key: "period", label: "Период", multi: false, options: ["Текущая неделя", "Текущий месяц"] },
    { key: "timeGrain", label: "Гранулярность", multi: false, options: ["Неделя", "Месяц"] },
    { key: "models", label: "Модели", multi: true, options: ["Reno10", "A78", "A58"] },
    { key: "metric", label: "Метрика", multi: false, options: ["₸", "Achv%"] },
    { key: "compare", label: "Сравнение", multi: true, options: ["WoW", "MoM"] },
    { key: "lfl", label: "LFL", multi: false, options: ["LFL вкл", "LFL выкл"] },
  ],
};

const kpiData = {
  admin: [
    { title: "Пользователи", value: "128", note: "активны за 7 дней" },
    { title: "Ошибки API", value: "3", note: "за 24 часа", variant: "danger" },
    { title: "Синхронизации", value: "12", note: "выполнено сегодня" },
  ],
  office: [
    { title: "План месяца", value: "₸ 180M", note: "Офис установил" },
    { title: "Факт", value: "₸ 132M", note: "73% выполнения" },
    { title: "Бонусный фонд", value: "₸ 8.4M", note: "доступно" },
  ],
  supervisor: [
    { title: "Регион Юг", value: "₸ 72M", note: "4 сети" },
    { title: "Топ магазин", value: "Mega Alma", note: "₸ 12.5M" },
    { title: "Промоутеры", value: "38", note: "активны" },
  ],
  promoter: [
    { title: "План месяца", value: "₸ 2.4M", note: "установил офис" },
    { title: "Факт", value: "₸ 1.86M", note: "78% выполнено" },
    { title: "Бонус к выплате", value: "₸ 180k", note: "после апрува" },
  ],
  trainer: [
    { title: "Сессии", value: "12", note: "в этом месяце" },
    { title: "Участники", value: "84", note: "план/факт совпал" },
    { title: "Оценка", value: "4.8", note: "средний рейтинг" },
  ],
};

const tableData = {
  training: seedTraining,
};

const lazyCityData = [
  { city: "Алматы", network: "Sulpak", stores: "18", promoters: "24", status: "Работает" },
  { city: "Астана", network: "Mechta", stores: "12", promoters: "16", status: "Работает" },
  { city: "Шымкент", network: "Technodom", stores: "9", promoters: "11", status: "Нужен выезд" },
  { city: "Караганда", network: "Mechta", stores: "6", promoters: "7", status: "Работает" },
];

const chartCopy = {
  overview: {
    day: "График: продажи по дням. Второй показатель ASP включается опцией.",
    week: "График: недельные продажи. Доступен сравнительный анализ.",
    month: "График: продажи по месяцам. Отображает накопленный итог.",
  },
  models: "Сравнение до 5 моделей. Цвета соответствуют легенде.",
  promoter: "Личные продажи по дням с плановой линией.",
};

const comparisonState = [
  { label: "WoW", value: "+4.2%", trend: "up" },
  { label: "MoM", value: "+1.8%", trend: "up" },
  { label: "YoY", value: "−3.4%", trend: "down" },
];

const statusData = {
  api: { value: "OK", note: "99.9% uptime" },
  db: { value: "OK", note: "Latency 22ms" },
  bi: { value: "OK", note: "Metabase green" },
};

let activePopover = null;
let activePopoverContext = null;
let activePopoverKey = null;
let activeModalTrigger = null;
let focusTrapListener = null;

const selectors = {
  dashboards: document.querySelectorAll("[data-role-panel]"),
  roleTabs: document.querySelectorAll(".role-tabs .tab-button"),
  kpiContainers: document.querySelectorAll("[data-kpi]"),
  tables: document.querySelectorAll("table.responsive-table"),
  filterRegions: document.querySelectorAll("[data-filter-context]"),
  analyticsTabs: document.querySelectorAll(".sub-tabs"),
  analyticsPanels: document.querySelectorAll("[data-panel]"),
  grainButtons: document.querySelectorAll(".grain-button"),
  secondaryToggle: document.querySelector("[data-secondary-axis]"),
  chartPlaceholders: document.querySelectorAll("[data-chart]"),
  comparisons: document.querySelector("[data-comparisons]"),
  legend: document.querySelector("[data-legend]"),
  modal: document.querySelector("[data-modal]"),
  modalBody: document.querySelector("[data-modal-body]"),
  modalBackdrop: document.querySelector("[data-modal-backdrop]"),
  lazySections: document.querySelectorAll("[data-lazy]"),
  networkBanner: document.querySelector("[data-network-banner]"),
  networkMessage: document.querySelector("[data-network-message]"),
  queueIndicators: document.querySelectorAll("[data-queue-count]"),
  syncButtons: document.querySelectorAll('[data-action="sync-now"]'),
  toastStack: document.querySelector("[data-toast-stack]"),
};

function resolveApiUrl(path) {
  if (!API_BASE) {
    return path;
  }
  try {
    const normalized = path.startsWith("/") ? path.slice(1) : path;
    const base = API_BASE.endsWith("/") ? API_BASE : `${API_BASE}/`;
    return new URL(normalized, base).toString();
  } catch (error) {
    console.warn("Не удалось построить URL API", path, error);
    return path;
  }
}

function wrapRequest(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function openDatabase() {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAMES.outbox)) {
        const outbox = db.createObjectStore(STORE_NAMES.outbox, { keyPath: "id" });
        outbox.createIndex("status", "status", { unique: false });
        outbox.createIndex("nextAttempt", "nextAttempt", { unique: false });
      }
      if (!db.objectStoreNames.contains(STORE_NAMES.sales)) {
        const sales = db.createObjectStore(STORE_NAMES.sales, { keyPath: "id" });
        sales.createIndex("month", "month", { unique: false });
        sales.createIndex("updatedAt", "updatedAt", { unique: false });
      }
      if (!db.objectStoreNames.contains(STORE_NAMES.plans)) {
        const plans = db.createObjectStore(STORE_NAMES.plans, { keyPath: "id" });
        plans.createIndex("month", "month", { unique: false });
        plans.createIndex("promoterId", "promoterId", { unique: false });
        plans.createIndex("updatedAt", "updatedAt", { unique: false });
      }
      if (!db.objectStoreNames.contains(STORE_NAMES.reference)) {
        db.createObjectStore(STORE_NAMES.reference, { keyPath: "key" });
      }
      if (!db.objectStoreNames.contains(STORE_NAMES.meta)) {
        db.createObjectStore(STORE_NAMES.meta, { keyPath: "key" });
      }
    };
    request.onsuccess = () => {
      const db = request.result;
      db.onversionchange = () => db.close();
      resolve(db);
    };
    request.onerror = () => reject(request.error);
  });
  return dbPromise;
}

async function idbRun(storeName, mode, executor) {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, mode);
    const store = tx.objectStore(storeName);
    let result;
    try {
      result = executor(store, tx);
    } catch (error) {
      reject(error);
      return;
    }
    if (result instanceof Promise) {
      result
        .then((value) => {
          tx.oncomplete = () => resolve(value);
        })
        .catch((error) => {
          reject(error);
          try {
            tx.abort();
          } catch (abortError) {
            console.warn("Не удалось прервать транзакцию", abortError);
          }
        });
    } else {
      tx.oncomplete = () => resolve(result);
    }
    tx.onabort = () => reject(tx.error || new Error("Transaction aborted"));
    tx.onerror = () => reject(tx.error || new Error("Transaction error"));
  });
}

function metaGet(key) {
  return idbRun(STORE_NAMES.meta, "readonly", (store) => wrapRequest(store.get(key))).then(
    (entry) => entry?.value ?? null
  );
}

function metaSet(key, value) {
  return idbRun(STORE_NAMES.meta, "readwrite", (store) => wrapRequest(store.put({ key, value })));
}

async function seedDatabase() {
  const currentSeed = await metaGet("seedVersion");
  if (currentSeed === SEED_VERSION) {
    return;
  }
  await idbRun(STORE_NAMES.sales, "readwrite", (store) => {
    seedSales.forEach((item) => store.put(item));
  });
  await idbRun(STORE_NAMES.plans, "readwrite", (store) => {
    seedPlans.forEach((item) => store.put(item));
  });
  await idbRun(STORE_NAMES.reference, "readwrite", (store) => {
    store.put({ key: "users", value: seedUsers });
    store.put({ key: "training", value: seedTraining });
  });
  await metaSet("watermark", offlineMetaSeed.watermark);
  await metaSet("seedVersion", SEED_VERSION);
}

async function loadOfflineCaches() {
  const sales =
    (await idbRun(STORE_NAMES.sales, "readonly", (store) => wrapRequest(store.getAll()))) || [];
  const plans =
    (await idbRun(STORE_NAMES.plans, "readonly", (store) => wrapRequest(store.getAll()))) || [];
  const referenceEntries =
    (await idbRun(STORE_NAMES.reference, "readonly", (store) => wrapRequest(store.getAll()))) || [];
  const referenceMap = Object.fromEntries(referenceEntries.map((entry) => [entry.key, entry.value]));
  offlineDataCache.sales = sales;
  offlineDataCache.plans = plans;
  offlineDataCache.users = Array.isArray(referenceMap.users) ? referenceMap.users : seedUsers;
  offlineDataCache.training = Array.isArray(referenceMap.training)
    ? referenceMap.training
    : seedTraining;
}

const outboxService = {
  async enqueue(entry) {
    const now = Date.now();
    const recordId = entry.id || (crypto.randomUUID ? crypto.randomUUID() : `${now}-${Math.random()}`);
    const payload = {
      url: entry.payload.url,
      method: entry.payload.method,
      body: entry.payload.body,
      headers: entry.payload.headers || {},
      collection: entry.payload.collection || null,
      localId: entry.payload.localId || null,
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
    await idbRun(STORE_NAMES.outbox, "readwrite", (store) => store.put(record));
    return record;
  },
  async countPending() {
    const records =
      (await idbRun(STORE_NAMES.outbox, "readonly", (store) => wrapRequest(store.getAll()))) || [];
    return records.filter((item) => item && item.status !== "sent").length;
  },
  async getReadyBatch(limit = QUEUE_BATCH_SIZE) {
    return idbRun(STORE_NAMES.outbox, "readonly", (store) =>
      new Promise((resolve, reject) => {
        const results = [];
        const index = store.index("nextAttempt");
        const range = IDBKeyRange.upperBound(Date.now());
        const request = index.openCursor(range);
        request.onsuccess = (event) => {
          const cursor = event.target.result;
          if (!cursor || results.length >= limit) {
            resolve(results);
            return;
          }
          const value = cursor.value;
          if (value.status === "queued") {
            results.push(value);
          }
          cursor.continue();
        };
        request.onerror = () => reject(request.error);
      })
    );
  },
  async update(id, updater) {
    return idbRun(STORE_NAMES.outbox, "readwrite", (store) =>
      new Promise((resolve, reject) => {
        const request = store.get(id);
        request.onsuccess = () => {
          const record = request.result;
          if (!record) {
            resolve(null);
            return;
          }
          const next = updater({ ...record }) || record;
          store.put(next).onsuccess = () => resolve(next);
        };
        request.onerror = () => reject(request.error);
      })
    );
  },
  markSending(id) {
    return this.update(id, (record) => ({
      ...record,
      status: "sending",
      nextAttempt: Date.now(),
    }));
  },
  markSent(id) {
    return this.update(id, (record) => ({
      ...record,
      status: "sent",
      retries: 0,
      nextAttempt: null,
      lastError: null,
    }));
  },
  markForRetry(id, retries, delay, lastError) {
    return this.update(id, (record) => ({
      ...record,
      status: "queued",
      retries,
      nextAttempt: Date.now() + delay,
      lastError,
    }));
  },
  markFailed(id, lastError) {
    return this.update(id, (record) => ({
      ...record,
      status: "failed",
      nextAttempt: null,
      lastError,
    }));
  },
  markConflict(id, payload) {
    return this.update(id, (record) => ({
      ...record,
      status: "conflict",
      nextAttempt: null,
      lastError: payload?.message || record.lastError,
      conflictPayload: payload || null,
    }));
  },
  async resetFailedToQueued() {
    const records =
      (await idbRun(STORE_NAMES.outbox, "readonly", (store) => wrapRequest(store.getAll()))) || [];
    const failed = records.filter((item) => item.status === "failed");
    if (!failed.length) return;
    await idbRun(STORE_NAMES.outbox, "readwrite", (store) => {
      failed.forEach((item) => {
        store.put({
          ...item,
          status: "queued",
          nextAttempt: Date.now(),
        });
      });
    });
  },
};

const networkIndicator = {
  init() {
    this.update();
  },
  update(message) {
    if (!selectors.networkBanner || !selectors.networkMessage) return;
    const online = navigator.onLine;
    if (!online) {
      selectors.networkMessage.textContent =
        message || "Нет сети. Изменения сохраняются локально.";
      selectors.networkBanner.dataset.status = "offline";
      selectors.networkBanner.hidden = false;
      return;
    }
    selectors.networkMessage.textContent = message || "Соединение восстановлено.";
    selectors.networkBanner.dataset.status = "online";
  },
  setQueue(count) {
    selectors.queueIndicators.forEach((node) => {
      node.textContent = `Очередь: ${count}`;
      node.dataset.count = String(count);
    });
    if (!selectors.networkBanner) return;
    if (count > 0) {
      selectors.networkBanner.hidden = false;
      selectors.networkBanner.dataset.status = navigator.onLine ? "online" : "offline";
      selectors.networkMessage.textContent = navigator.onLine
        ? `В очереди ${count} запрос(ов).`
        : `Оффлайн. В очереди ${count} запрос(ов).`;
    } else if (navigator.onLine) {
      selectors.networkMessage.textContent = "Очередь пуста.";
      selectors.networkBanner.dataset.status = "online";
      setTimeout(() => {
        const currentCount = Number(selectors.queueIndicators[0]?.dataset.count || 0);
        if (navigator.onLine && currentCount === 0) {
          selectors.networkBanner.hidden = true;
        }
      }, 2600);
    }
  },
};

const toastManager = {
  stack: null,
  init() {
    this.stack = selectors.toastStack;
  },
  show(kind, title, message) {
    if (!this.stack) return;
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.dataset.kind = kind;
    toast.innerHTML = `
      <p class="toast__title">${title}</p>
      <p class="toast__message">${message}</p>
    `;
    this.stack.append(toast);
    setTimeout(() => {
      toast.classList.add("is-leaving");
      setTimeout(() => toast.remove(), 220);
    }, 4000);
  },
  success(title, message) {
    this.show("success", title, message);
  },
  info(title, message) {
    this.show("info", title, message);
  },
  warning(title, message) {
    this.show("warning", title, message);
  },
  error(title, message) {
    this.show("error", title, message);
  },
};

const offlineController = {
  async init() {
    await seedDatabase();
    await loadOfflineCaches();
    await this.refreshQueueCount();
  },
  async refreshQueueCount() {
    const count = await outboxService.countPending();
    networkIndicator.setQueue(count);
    return count;
  },
  async reloadAndRender() {
    await loadOfflineCaches();
    await populateTables();
    await renderChartCopy();
  },
  async getRowsFor(source) {
    switch (source) {
      case "plans":
        return buildPlanRows(offlineDataCache.plans);
      case "plans-monthly":
        return buildMonthlyPlanRows(offlineDataCache.plans);
      case "users":
        return buildUserRows(offlineDataCache.users);
      default:
        return [];
    }
  },
  async markLocalStatus(collection, id, status, details = {}) {
    if (!collection || !id) return;
    const storeName = STORE_NAMES[collection];
    if (!storeName) return;
    await idbRun(storeName, "readwrite", (store) =>
      new Promise((resolve, reject) => {
        const request = store.get(id);
        request.onsuccess = () => {
          const record = request.result;
          if (!record) {
            resolve();
            return;
          }
          const next = {
            ...record,
            syncStatus: status,
            lastError: details.lastError ?? record.lastError ?? null,
            conflict: status === "conflict",
          };
          if (details.serverSnapshot) {
            next.serverSnapshot = details.serverSnapshot;
          }
          if (details.updatedAt) {
            next.updatedAt = details.updatedAt;
          }
          store.put(next).onsuccess = () => resolve();
        };
        request.onerror = () => reject(request.error);
      })
    );
    await this.reloadAndRender();
  },
};

const analyticsLoader = {
  cache: {
    sales: [],
    plans: [],
  },
  refreshCache() {
    this.cache.sales = offlineDataCache.sales.slice();
    this.cache.plans = offlineDataCache.plans.slice();
  },
  sumByGrain(grain) {
    const sales = this.cache.sales;
    if (!sales.length) return null;
    const buckets = new Map();
    sales.forEach((sale) => {
      const date = new Date(sale.date);
      if (Number.isNaN(date.getTime())) return;
      let key;
      if (grain === "week") {
        const week = getWeekNumber(date);
        key = `${date.getFullYear()}-W${week}`;
      } else if (grain === "month") {
        key = sale.month || `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
      } else {
        key = sale.date;
      }
      const bucket = buckets.get(key) || { amount: 0, quantity: 0 };
      bucket.amount += sale.amount || 0;
      bucket.quantity += sale.quantity || 0;
      buckets.set(key, bucket);
    });
    return {
      buckets,
      total: Array.from(buckets.values()).reduce((acc, item) => acc + item.amount, 0),
      entries: buckets.size,
    };
  },
  getOverviewCopy(grain) {
    const summary = this.sumByGrain(grain);
    if (!summary) {
      return navigator.onLine ? "Ожидание данных от сервера." : "Нет данных в оффлайн-хранилище.";
    }
    const amount = formatCurrencyKZT(summary.total);
    const label = grain === "day" ? "дней" : grain === "week" ? "недель" : "месяцев";
    const offlineMark = navigator.onLine ? "" : " · оффлайн";
    return `Локально: ${amount} за ${summary.entries} ${label}${offlineMark}.`;
  },
  getModelsCopy() {
    if (!this.cache.plans.length) {
      return navigator.onLine ? chartCopy.models : "Нет планов в оффлайн-хранилище.";
    }
    const sorted = [...this.cache.plans].sort((a, b) => (b.fact || 0) - (a.fact || 0));
    const top = sorted.slice(0, 3);
    const description = top
      .map((plan) => `${plan.store}: ${formatCurrencyKZT(plan.fact || 0)}`)
      .join(" · ");
    return `Топ магазинов по факту: ${description}.`;
  },
  getPromoterCopy() {
    if (!this.cache.plans.length) {
      return navigator.onLine ? chartCopy.promoter : "Нет планов промоутера в оффлайне.";
    }
    const promoterPlans = this.cache.plans.filter((plan) => plan.promoterId === "promoter-001");
    if (!promoterPlans.length) {
      return chartCopy.promoter;
    }
    const totalPlan = promoterPlans.reduce((sum, item) => sum + (item.plan || 0), 0);
    const totalFact = promoterPlans.reduce((sum, item) => sum + (item.fact || 0), 0);
    const achv = totalPlan ? totalFact / totalPlan : 0;
    return `Личный план: ${formatCurrencyKZT(totalPlan)} · факт ${formatCurrencyKZT(totalFact)} (${formatPercentValue(achv)}).`;
  },
};

const syncEngine = {
  isSyncing: false,
  lastSync: 0,
  pending: false,
  async manual() {
    toastManager.info("Синхронизация", "Запуск ручной синхронизации...");
    await outboxService.resetFailedToQueued();
    await this.run("manual");
  },
  async auto(reason) {
    const now = Date.now();
    if (reason !== "manual" && now - this.lastSync < 5000) {
      return;
    }
    await this.run(reason);
  },
  async run(reason) {
    if (this.isSyncing) {
      this.pending = true;
      return;
    }
    if (!navigator.onLine && reason !== "manual") {
      return;
    }
    this.isSyncing = true;
    try {
      await this.pushOutbox();
      if (navigator.onLine) {
        const pulled = await this.pullChanges();
        if (pulled) {
          toastManager.success("Данные обновлены", "Сервер прислал изменения.");
        }
      }
    } catch (error) {
      console.error("Sync error", error);
      toastManager.error("Ошибка синхронизации", error.message || "Неизвестная ошибка");
    } finally {
      this.isSyncing = false;
      this.lastSync = Date.now();
      await offlineController.refreshQueueCount();
      if (this.pending) {
        this.pending = false;
        setTimeout(() => this.auto("chain"), 500);
      }
    }
  },
  async pushOutbox() {
    analyticsLoader.refreshCache();
    let batch = await outboxService.getReadyBatch();
    while (batch.length) {
      for (const record of batch) {
        await outboxService.markSending(record.id);
        if (record.payload.collection && record.payload.localId) {
          await offlineController.markLocalStatus(
            record.payload.collection,
            record.payload.localId,
            "sending",
            { updatedAt: new Date().toISOString() }
          );
        }
      try {
        const response = await sendOutboxRecord(record);
        if (response.status === 409) {
          const serverPayload = await safeJson(response);
          await outboxService.markConflict(record.id, {
            message: "Конфликт версий",
            payload: serverPayload,
          });
          if (record.payload.collection && record.payload.localId) {
            await offlineController.markLocalStatus(
              record.payload.collection,
              record.payload.localId,
              "conflict",
              {
                serverSnapshot: serverPayload,
                lastError: "Конфликт версий",
              }
            );
          }
          toastManager.warning("Конфликт", "Данные на сервере отличаются. Нужна сверка.");
          continue;
        }
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        await outboxService.markSent(record.id);
        if (record.payload.collection && record.payload.localId) {
          await offlineController.markLocalStatus(
            record.payload.collection,
            record.payload.localId,
            "sent",
            { updatedAt: new Date().toISOString() }
          );
        }
        toastManager.success("Синхронизировано", "Очередной запрос обработан.");
      } catch (error) {
        const retries = (record.retries || 0) + 1;
        if (retries >= MAX_RETRIES) {
          await outboxService.markFailed(record.id, error.message);
          if (record.payload.collection && record.payload.localId) {
            await offlineController.markLocalStatus(
              record.payload.collection,
              record.payload.localId,
              "failed",
              { lastError: error.message }
            );
          }
          toastManager.error("Не удалось отправить", "Проверьте запись и повторите.");
        } else {
          const delay = Math.min(RETRY_BASE_DELAY * Math.pow(2, retries - 1), 5 * 60 * 1000);
          await outboxService.markForRetry(record.id, retries, delay, error.message);
          if (record.payload.collection && record.payload.localId) {
            await offlineController.markLocalStatus(
              record.payload.collection,
              record.payload.localId,
              "queued",
              { lastError: error.message }
            );
          }
          toastManager.warning("Перенос попытки", "Запрос останется в очереди.");
          }
        }
      }
      batch = await outboxService.getReadyBatch();
    }
  },
  async pullChanges() {
    if (!API_BASE) {
      return false;
    }
    const since = (await metaGet("watermark")) || "";
    const url = resolveApiUrl(`/sync/changes?since=${encodeURIComponent(since)}`);
    let response;
    try {
      response = await fetch(url, {
        method: "GET",
        headers: { Accept: "application/json" },
        credentials: "include",
      });
    } catch (error) {
      console.warn("Pull failed", error);
      return false;
    }
    if (!response.ok) {
      throw new Error(`Pull failed: ${response.status}`);
    }
    const payload = await safeJson(response);
    if (!payload || typeof payload !== "object") {
      return false;
    }
    const { sales = [], plans = [], users = [], reference = {}, watermark } = payload;
    if (Array.isArray(sales) && sales.length) {
      await idbRun(STORE_NAMES.sales, "readwrite", (store) => {
        sales.forEach((item) => {
          store.put({
            ...item,
            syncStatus: "sent",
            updatedAt: item.updatedAt || new Date().toISOString(),
          });
        });
      });
    }
    if (Array.isArray(plans) && plans.length) {
      await idbRun(STORE_NAMES.plans, "readwrite", (store) => {
        plans.forEach((item) => {
          store.put({
            ...item,
            syncStatus: item.conflict ? "conflict" : "sent",
            updatedAt: item.updatedAt || new Date().toISOString(),
          });
        });
      });
    }
    if (Array.isArray(users) && users.length) {
      await idbRun(STORE_NAMES.reference, "readwrite", (store) => {
        store.put({ key: "users", value: users });
      });
    }
    if (reference.training) {
      await idbRun(STORE_NAMES.reference, "readwrite", (store) => {
        store.put({ key: "training", value: reference.training });
      });
    }
    if (watermark) {
      await metaSet("watermark", watermark);
    }
    await offlineController.reloadAndRender();
    return true;
  },
};

const apiClient = {
  async mutate({ method, path, body, type, localCollection, localId }) {
    const url = resolveApiUrl(path);
    const idempotencyKey =
      (body && body.id) || (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()));
    const headers = {
      "Content-Type": "application/json",
      Accept: "application/json",
      "Idempotency-Key": idempotencyKey,
      "X-Offline-Type": type,
    };
    if (localCollection) {
      headers["X-Offline-Collection"] = localCollection;
    }
    if (localId) {
      headers["X-Offline-Id"] = localId;
    }
    const payload = body ? JSON.stringify(body) : undefined;
    try {
      const response = await fetch(url, {
        method,
        headers,
        body: payload,
        credentials: "include",
      });
      if (response.status === 202) {
        await offlineController.refreshQueueCount();
        toastManager.info("Сохранено локально", "Запрос в очереди на синхронизацию.");
        return { queued: true };
      }
      if (response.status === 409) {
        const serverPayload = await safeJson(response);
        await offlineController.markLocalStatus(localCollection, localId, "conflict", {
          serverSnapshot: serverPayload,
          lastError: "Конфликт версий",
        });
        toastManager.warning("Конфликт", "Сервер уже изменил запись.");
        return { conflict: true };
      }
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await safeJson(response);
      if (localCollection && localId) {
        await offlineController.markLocalStatus(localCollection, localId, "sent", {
          updatedAt: new Date().toISOString(),
        });
      }
      toastManager.success("Обновлено", "Запрос выполнен на сервере.");
      return data;
    } catch (error) {
      await outboxService.enqueue({
        id: idempotencyKey,
        type,
        payload: {
          url,
          method,
          body,
          headers: sanitizeHeaders(headers),
          collection: localCollection,
          localId,
          idempotencyKey,
        },
        lastError: error.message,
      });
      if (localCollection && localId) {
        await offlineController.markLocalStatus(localCollection, localId, "queued", {
          lastError: error.message,
        });
      }
      await offlineController.refreshQueueCount();
      toastManager.info("Сохранено локально", "Синхронизация выполнится при доступе к сети.");
      swBridge.requestBackgroundSync();
      return { queued: true };
    }
  },
};

const swBridge = {
  registration: null,
  async register() {
    if (!("serviceWorker" in navigator)) return;
    const isSecure =
      window.location.protocol === "https:" || window.location.hostname === "localhost";
    if (!isSecure) return;
    try {
      this.registration = await navigator.serviceWorker.register(SERVICE_WORKER_PATH, {
        scope: "./",
      });
      navigator.serviceWorker.addEventListener("message", (event) => {
        const { type, payload } = event.data || {};
        handleServiceWorkerMessage(type, payload);
      });
    } catch (error) {
      console.warn("SW registration failed", error);
    }
  },
  requestBackgroundSync() {
    if (this.registration && "sync" in this.registration) {
      this.registration.sync.register("oppo-sync").catch((error) => {
        console.warn("Background sync registration failed", error);
      });
    }
  },
};

function sanitizeHeaders(headers) {
  const allowed = [
    "Content-Type",
    "Accept",
    "X-Offline-Type",
    "X-Offline-Collection",
    "X-Offline-Id",
    "Idempotency-Key",
  ];
  return Object.fromEntries(Object.entries(headers).filter(([key]) => allowed.includes(key)));
}

async function sendOutboxRecord(record) {
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
  if (body && typeof rawBody !== "string" && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return fetch(record.payload.url, {
    method: record.payload.method,
    headers,
    body,
    credentials: "include",
  });
}

async function safeJson(response) {
  try {
    return await response.json();
  } catch (error) {
    return null;
  }
}

function formatCurrencyKZT(value) {
  const number = Number(value) || 0;
  return `₸ ${Math.round(number).toLocaleString("ru-RU")}`;
}

function formatPercentValue(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "0%";
  }
  return `${(value * 100).toFixed(1)}%`;
}

function formatDateTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value || "—";
  }
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatRelativeTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  const diffMs = Date.now() - date.getTime();
  const diffMinutes = Math.round(diffMs / 60000);
  if (diffMinutes < 1) return "только что";
  if (diffMinutes < 60) return `${diffMinutes} мин назад`;
  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours} ч назад`;
  const diffDays = Math.round(diffHours / 24);
  if (diffDays < 30) return `${diffDays} дн назад`;
  return date.toLocaleDateString("ru-RU");
}

function formatMonthLabel(month) {
  if (!month) return "—";
  const [year, monthPart] = month.split("-");
  const index = Number(monthPart) - 1;
  if (Number.isNaN(index) || index < 0 || index > 11) {
    return month;
  }
  return `${monthNames[index]} ${year}`;
}

function getWeekNumber(date) {
  const tmp = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = tmp.getUTCDay() || 7;
  tmp.setUTCDate(tmp.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(tmp.getUTCFullYear(), 0, 1));
  return Math.ceil(((tmp - yearStart) / 86400000 + 1) / 7);
}

function pickDominantStatus(current, next) {
  const currentPriority = syncStatusPriority[current] || 0;
  const nextPriority = syncStatusPriority[next] || 0;
  return nextPriority > currentPriority ? next : current;
}

function buildPlanRows(plans) {
  return plans.map((plan) => {
    const achv = plan.plan ? plan.fact / plan.plan : 0;
    const status = plan.syncStatus || "sent";
    const note = plan.conflict
      ? "Требуется сверка"
      : plan.lastError
      ? plan.lastError
      : `Обновлено ${formatRelativeTime(plan.updatedAt)}`;
    return {
      syncStatus: status,
      columns: [
        { value: plan.store },
        { value: plan.promoter },
        { value: formatCurrencyKZT(plan.plan) },
        { value: formatCurrencyKZT(plan.fact) },
        { value: formatPercentValue(achv) },
        { value: formatCurrencyKZT(plan.bonus) },
        {
          value: {
            type: "status",
            status,
            label: syncStatusLabels[status] || status,
            note,
          },
        },
      ],
    };
  });
}

function buildMonthlyPlanRows(plans) {
  const map = new Map();
  plans.forEach((plan) => {
    if (plan.promoterId !== "promoter-001") return;
    const key = plan.month;
    const entry = map.get(key) || {
      plan: 0,
      fact: 0,
      bonus: 0,
      status: "sent",
      notes: [],
    };
    entry.plan += plan.plan || 0;
    entry.fact += plan.fact || 0;
    entry.bonus += plan.bonus || 0;
    entry.status = pickDominantStatus(entry.status, plan.syncStatus || "sent");
    if (plan.conflict) {
      entry.notes.push("Есть конфликт");
    }
    if (plan.lastError) {
      entry.notes.push(plan.lastError);
    }
    entry.updatedAt = plan.updatedAt;
    map.set(key, entry);
  });
  return Array.from(map.entries())
    .sort(([a], [b]) => (a > b ? -1 : 1))
    .map(([month, entry]) => ({
      syncStatus: entry.status,
      columns: [
        { value: formatMonthLabel(month) },
        { value: formatCurrencyKZT(entry.plan) },
        { value: formatCurrencyKZT(entry.fact) },
        { value: formatPercentValue(entry.plan ? entry.fact / entry.plan : 0) },
        { value: formatCurrencyKZT(entry.bonus) },
        {
          value: {
            type: "status",
            status: entry.status,
            label: syncStatusLabels[entry.status] || entry.status,
            note: entry.notes.join("; ") || `Обновлено ${formatRelativeTime(entry.updatedAt)}`,
          },
        },
      ],
    }));
}

function buildUserRows(users) {
  return users.map((user) => {
    const status = user.syncStatus || "sent";
    const accountLabel = accountStatusLabels[user.accountStatus] || user.accountStatus;
    const note = user.lastError ? user.lastError : `Обновлено ${formatRelativeTime(user.lastLogin)}`;
    return {
      syncStatus: status,
      columns: [
        { value: user.name },
        { value: user.role },
        { value: user.region },
        { value: formatDateTime(user.lastLogin) },
        {
          value: {
            type: "statusText",
            text: accountLabel,
            status,
            note,
          },
        },
      ],
    };
  });
}

function createCellContent(cell) {
  if (cell && typeof cell === "object") {
    if (cell.type === "status") {
      const badge = document.createElement("span");
      badge.className = "status-badge";
      badge.dataset.status = cell.status;
      badge.textContent = cell.label || syncStatusLabels[cell.status] || cell.status;
      if (cell.note) {
        badge.title = cell.note;
      }
      return badge;
    }
    if (cell.type === "statusText") {
      const wrapper = document.createElement("span");
      wrapper.className = "cell-status";
      const text = document.createElement("span");
      text.className = "cell-status__text";
      text.textContent = cell.text;
      const badge = document.createElement("span");
      badge.className = "status-badge";
      badge.dataset.status = cell.status;
      badge.textContent = syncStatusLabels[cell.status] || cell.status;
      if (cell.note) badge.title = cell.note;
      wrapper.append(text, badge);
      return wrapper;
    }
    if (cell.value !== undefined) {
      return document.createTextNode(String(cell.value));
    }
  }
  if (cell === null || cell === undefined || cell === "") {
    return document.createTextNode("—");
  }
  return document.createTextNode(cell);
}

function renderTableRows(table, rows) {
  const tbody = table.querySelector("tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const columns = Array.isArray(row?.columns)
      ? row.columns
      : Object.values(row).map((value) => ({ value }));
    columns.forEach((column) => {
      const td = document.createElement("td");
      const content = createCellContent(column);
      if (content instanceof Node) {
        td.append(content);
      } else {
        td.textContent = content;
      }
      tr.append(td);
    });
    if (row.syncStatus) {
      tr.dataset.syncStatus = row.syncStatus;
    }
    tbody.append(tr);
  });
}

function getFallbackTableRows(key) {
  const rows = tableData[key] || [];
  return rows.map((row) => ({
    columns: Object.values(row).map((value) => ({ value })),
  }));
}

function handleServiceWorkerMessage(type, payload) {
  switch (type) {
    case "outbox:queued":
      offlineController.refreshQueueCount();
      toastManager.info("Сохранено локально", "Запрос помещён в очередь.");
      break;
    case "outbox:sent":
      offlineController.refreshQueueCount();
      toastManager.success("Отправлено", "Очередь сократилась.");
      break;
    case "outbox:failed": {
      offlineController.refreshQueueCount();
      if (payload?.status === "conflict") {
        toastManager.warning("Конфликт", payload?.message || "Нужна сверка с сервером.");
      } else {
        toastManager.error("Ошибка синхронизации", payload?.message || "");
      }
      break;
    }
    case "sync:trigger":
      syncEngine.auto("sw");
      break;
    case "sync:complete":
      offlineController.reloadAndRender();
      offlineController.refreshQueueCount();
      toastManager.success("Обновлено", "Фоновые данные доставлены.");
      break;
    default:
      break;
  }
}

function renderAllKpis() {
  selectors.kpiContainers.forEach((container) => {
    const key = container.dataset.kpi;
    container.innerHTML = "";
    (kpiData[key] || []).forEach((item) => {
      const card = document.createElement("article");
      card.className = "kpi-card";
      if (item.variant) {
        card.dataset.variant = item.variant;
      }
      card.innerHTML = `
        <h3>${item.title}</h3>
        <p class="kpi-value">${item.value}</p>
        <p class="kpi-note">${item.note}</p>
      `;
      container.append(card);
    });
  });
}

async function populateTables() {
  const tasks = Array.from(selectors.tables).map(async (table) => {
    const key = table.dataset.table;
    const source = table.dataset.source;
    const rows = source ? await offlineController.getRowsFor(source) : getFallbackTableRows(key);
    renderTableRows(table, rows);
  });
  await Promise.all(tasks);
}

function enhanceTables() {
  selectors.tables.forEach((table) => {
    const headers = Array.from(table.querySelectorAll("thead th"));
    const rows = table.querySelectorAll("tbody tr");
    rows.forEach((row) => {
      Array.from(row.children).forEach((cell, index) => {
        const label = headers[index]?.textContent?.trim() ?? "";
        const priority = headers[index]?.dataset.priority ?? "primary";
        cell.setAttribute("data-label", label);
        cell.dataset.priority = priority;
      });
    });
    headers.forEach((th, index) => {
      th.addEventListener("click", () => handleSort(table, index));
    });
  });
}

function handleSort(table, columnIndex) {
  if (window.matchMedia("(max-width: 768px)").matches) {
    return;
  }
  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const isNumeric = rows.every((row) => {
    const text = row.children[columnIndex]?.textContent?.replace(/[^0-9.-]/g, "");
    return text !== "";
  });
  const current = table.dataset.sortColumn === String(columnIndex) ? table.dataset.sortDir : "asc";
  const nextDir = current === "asc" ? "desc" : "asc";
  const sorted = rows.sort((a, b) => {
    const aText = a.children[columnIndex]?.textContent ?? "";
    const bText = b.children[columnIndex]?.textContent ?? "";
    if (isNumeric) {
      const aNum = parseFloat(aText.replace(/[^0-9.-]/g, "")) || 0;
      const bNum = parseFloat(bText.replace(/[^0-9.-]/g, "")) || 0;
      return nextDir === "asc" ? aNum - bNum : bNum - aNum;
    }
    return nextDir === "asc" ? aText.localeCompare(bText) : bText.localeCompare(aText);
  });
  tbody.innerHTML = "";
  sorted.forEach((row) => tbody.append(row));
  table.dataset.sortColumn = String(columnIndex);
  table.dataset.sortDir = nextDir;
}

function setupRoleTabs() {
  selectors.roleTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const role = tab.dataset.role;
      if (role === state.currentRole) return;
      state.currentRole = role;
      selectors.roleTabs.forEach((btn) => btn.classList.toggle("is-active", btn === tab));
      selectors.dashboards.forEach((panel) => {
        panel.classList.toggle("is-hidden", panel.dataset.rolePanel !== role);
      });
      document.getElementById("main").focus();
    });
  });
}

function setupAnalyticsTabs() {
  selectors.analyticsTabs.forEach((nav) => {
    const buttons = nav.querySelectorAll(".sub-tab-button");
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        buttons.forEach((btn) => btn.classList.toggle("is-active", btn === button));
        const target = button.dataset.target;
        const parent = nav.closest(".analytics");
        parent.querySelectorAll("[data-panel]").forEach((panel) => {
          panel.classList.toggle("is-hidden", panel.dataset.panel !== target);
        });
      });
    });
  });
}

function setupFilters() {
  selectors.filterRegions.forEach((region) => {
    const context = region.dataset.filterContext;
    const controlsContainer = region.querySelector("[data-filter-controls]");
    const chipsContainer = region.querySelector("[data-filter-chips]");
    controlsContainer.innerHTML = "";
    filtersConfig[context].forEach((filter) => {
      const trigger = document.createElement("button");
      trigger.type = "button";
      trigger.className = "filter-trigger";
      trigger.dataset.filterKey = filter.key;
      trigger.textContent = filter.label;
      trigger.addEventListener("click", (event) => {
        event.stopPropagation();
        togglePopover(event.currentTarget, context, filter);
      });
      controlsContainer.append(trigger);
    });
    updateFilterChips(context, chipsContainer);
  });

  document.addEventListener("click", (event) => {
    if (
      activePopover &&
      !activePopover.contains(event.target) &&
      event.target !== activePopover.trigger
    ) {
      activePopover.remove();
      activePopover = null;
      activePopoverContext = null;
      activePopoverKey = null;
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && activePopover) {
      activePopover.remove();
      activePopover = null;
      activePopoverContext = null;
      activePopoverKey = null;
    }
  });

  document.querySelectorAll('[data-action="clear-filters"]').forEach((button) => {
    button.addEventListener("click", () => {
      const context = button.closest("[data-filter-context]").dataset.filterContext;
      const chips = button.closest("[data-filter-context]").querySelector("[data-filter-chips]");
      Object.keys(state.filters[context]).forEach((key) => {
        state.filters[context][key] = [];
      });
      updateFilterChips(context, chips);
    });
  });
}

function togglePopover(trigger, context, filter) {
  if (activePopover) {
    activePopover.remove();
    activePopover = null;
    activePopoverContext = null;
    activePopoverKey = null;
  }
  const popover = document.createElement("div");
  popover.className = "filter-popover";
  popover.dataset.filterKey = filter.key;
  popover.trigger = trigger;
  popover.append(renderPopover(filter, context));
  const rect = trigger.getBoundingClientRect();
  popover.style.top = `${rect.bottom + window.scrollY + 8}px`;
  popover.style.left = `${rect.left + window.scrollX}px`;
  document.body.append(popover);
  activePopover = popover;
  activePopoverContext = context;
  activePopoverKey = filter.key;
}

function renderPopover(filter, context) {
  const list = document.createElement("div");
  list.className = "filter-options";
  filter.options.forEach((option) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "filter-option";
    const isActive = state.filters[context][filter.key]?.includes(option);
    item.setAttribute("aria-pressed", String(isActive));
    item.textContent = option;
    item.addEventListener("click", () => {
      const current = state.filters[context][filter.key] || [];
      if (filter.multi) {
        state.filters[context][filter.key] = isActive
          ? current.filter((value) => value !== option)
          : [...current, option];
      } else {
        state.filters[context][filter.key] = isActive ? [] : [option];
      }
      updateFilterChips(
        context,
        document
          .querySelector(`[data-filter-context="${context}"]`)
          .querySelector("[data-filter-chips]")
      );
      item.setAttribute("aria-pressed", String(!isActive));
    });
    list.append(item);
  });
  return list;
}

function updateFilterChips(context, container) {
  container.innerHTML = "";
  Object.entries(state.filters[context]).forEach(([key, values]) => {
    values.forEach((value) => {
      const chip = document.createElement("span");
      chip.className = "filter-chip";
      chip.innerHTML = `
        <span>${value}</span>
        <button type="button" aria-label="Удалить ${value}">×</button>
      `;
      chip.querySelector("button").addEventListener("click", () => {
        state.filters[context][key] = state.filters[context][key].filter((item) => item !== value);
        updateFilterChips(context, container);
      });
      container.append(chip);
    });
  });
}

function setupTableFilters() {
  document.querySelectorAll(".mobile-table-filter input").forEach((input) => {
    if (input.dataset.bound === "true") return;
    const tableKey = input.closest(".mobile-table-filter").dataset.filterFor;
    const table = document.querySelector(`table[data-table="${tableKey}"] tbody`);
    input.addEventListener("input", () => {
      const query = input.value.toLowerCase();
      if (!table) return;
      Array.from(table.querySelectorAll("tr")).forEach((row) => {
        const visible = row.textContent.toLowerCase().includes(query);
        row.style.display = visible ? "" : "none";
      });
    });
    input.dataset.bound = "true";
  });
}

function setupGrainSwitch() {
  selectors.grainButtons.forEach((button) => {
    button.addEventListener("click", () => {
      selectors.grainButtons.forEach((btn) => btn.classList.toggle("is-active", btn === button));
      state.chart.grain = button.dataset.grain;
      renderChartCopy();
    });
  });
  if (selectors.secondaryToggle) {
    selectors.secondaryToggle.addEventListener("change", (event) => {
      state.chart.secondaryAxis = Boolean(event.target.checked);
      renderChartCopy();
    });
  }
  renderChartCopy();
}

function renderChartCopy() {
  analyticsLoader.refreshCache();
  selectors.chartPlaceholders.forEach((placeholder) => {
    const key = placeholder.dataset.chart;
    if (key === "overview") {
      const grainCopy = analyticsLoader.getOverviewCopy(state.chart.grain);
      const axis = state.chart.secondaryAxis ? " Включена вторая ось ASP." : "";
      placeholder.textContent = `${grainCopy}${axis}`;
    } else if (key === "models") {
      placeholder.textContent = analyticsLoader.getModelsCopy();
    } else if (key === "promoter") {
      placeholder.textContent = analyticsLoader.getPromoterCopy();
    } else {
      placeholder.textContent = chartCopy[key] || "";
    }
  });
}

function setupComparisons() {
  if (!selectors.comparisons) return;
  selectors.comparisons.innerHTML = "";
  comparisonState.forEach((item) => {
    const chip = document.createElement("span");
    chip.className = "comparison-chip";
    chip.dataset.trend = item.trend;
    chip.textContent = `${item.label}: ${item.value}`;
    selectors.comparisons.append(chip);
  });
}

function setupLegend() {
  if (!selectors.legend) return;
  const colors = ["#22c55e", "#38bdf8", "#f97316", "#a855f7", "#facc15"];
  const models = filtersConfig.office.find((item) => item.key === "models").options.slice(0, 5);
  selectors.legend.innerHTML = "";
  models.forEach((model, index) => {
    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `
      <span class="legend-swatch" style="background:${colors[index % colors.length]}"></span>
      <span>${model}</span>
    `;
    selectors.legend.append(item);
  });
}

function setupMapMarkers() {
  const markers = document.querySelectorAll(".map-marker");
  markers.forEach((marker) => {
    marker.setAttribute("tabindex", "0");
    const showDetails = (event) => {
      event.preventDefault();
      const city = marker.dataset.city;
      const region = marker.dataset.region;
      openModal(
        `<p><strong>${city}</strong></p><p>Регион: ${region}</p><p>Оборот за месяц: ₸ ${(Math.random() * 12 + 3).toFixed(1)}M</p>`,
        `Магазины · ${city}`,
        marker
      );
    };
    marker.addEventListener("click", showDetails);
    marker.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        showDetails(event);
      }
    });
  });

  const isTouch = matchMedia("(pointer: coarse)").matches;
  if (isTouch) {
    markers.forEach((marker) => {
      marker.classList.add("touch-target");
    });
  }
}

function setupLazyLoading() {
  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          if (entry.target.dataset.lazy === "cities") {
            renderCityTable(entry.target.querySelector("[data-lazy-target]"));
          }
          obs.unobserve(entry.target);
        }
      });
    },
    {
      rootMargin: "200px 0px",
    }
  );
  selectors.lazySections.forEach((section) => observer.observe(section));
}

function renderCityTable(container) {
  const template = document.getElementById("city-table-template");
  if (!template) return;
  const fragment = template.content.cloneNode(true);
  const tbody = fragment.querySelector("tbody");
  lazyCityData.forEach((row) => {
    const tr = document.createElement("tr");
    Object.values(row).forEach((value) => {
      const td = document.createElement("td");
      td.textContent = value;
      tr.append(td);
    });
    tbody.append(tr);
  });
  container.innerHTML = "";
  container.append(fragment);
  enhanceTables();
  setupTableFilters();
}

function hydrateStatuses() {
  Object.entries(statusData).forEach(([key, payload]) => {
    const valueEl = document.querySelector(`[data-status="${key}"]`);
    if (!valueEl) return;
    valueEl.textContent = payload.value;
    const noteEl = valueEl.nextElementSibling;
    if (noteEl) {
      noteEl.textContent = payload.note;
    }
  });
}

function setupModalClose() {
  const modal = selectors.modal;
  const closeButtons = modal.querySelectorAll("[data-modal-close]");
  closeButtons.forEach((button) => button.addEventListener("click", closeModal));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hasAttribute("hidden")) {
      closeModal();
    }
  });
}

function openModal(content, title, trigger) {
  const modal = selectors.modal;
  const backdrop = selectors.modalBackdrop;
  selectors.modalBody.innerHTML = content;
  modal.querySelector("#modal-title").textContent = title;
  activeModalTrigger = trigger instanceof HTMLElement ? trigger : null;
  const isSheet = window.matchMedia("(max-width: 768px)").matches;
  modal.dataset.mode = isSheet ? "sheet" : "dialog";
  modal.setAttribute("open", "");
  modal.removeAttribute("hidden");
  backdrop.hidden = false;
  backdrop.dataset.active = "true";
  document.body.style.overflow = "hidden";
  const focusable = modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  const trap = (event) => {
    if (event.key !== "Tab") return;
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };
  focusTrapListener = trap;
  document.addEventListener("keydown", focusTrapListener);
  if (first) first.focus();
}

function closeModal() {
  const modal = selectors.modal;
  const backdrop = selectors.modalBackdrop;
  modal.setAttribute("hidden", "");
  modal.removeAttribute("open");
  modal.removeAttribute("data-mode");
  backdrop.hidden = true;
  backdrop.dataset.active = "false";
  selectors.modalBody.innerHTML = "";
  document.body.style.overflow = "";
  if (focusTrapListener) {
    document.removeEventListener("keydown", focusTrapListener);
    focusTrapListener = null;
  }
  if (activeModalTrigger instanceof HTMLElement) {
    activeModalTrigger.focus();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  (async () => {
    toastManager.init();
    networkIndicator.init();
    await offlineController.init();
    analyticsLoader.refreshCache();
    renderAllKpis();
    await populateTables();
    enhanceTables();
    hydrateStatuses();
    setupRoleTabs();
    setupAnalyticsTabs();
    setupFilters();
    setupTableFilters();
    setupGrainSwitch();
    setupComparisons();
    setupLegend();
    setupMapMarkers();
    setupLazyLoading();
    setupModalClose();
    selectors.syncButtons.forEach((button) => {
      button.addEventListener("click", () => syncEngine.manual());
    });
    window.addEventListener("online", () => {
      networkIndicator.update();
      toastManager.success("Онлайн", "Соединение восстановлено.");
      syncEngine.auto("online");
    });
    window.addEventListener("offline", () => {
      networkIndicator.update("Нет сети. Изменения сохраняются локально.");
      toastManager.warning("Оффлайн", "Работаем с локальными данными.");
    });
    window.addEventListener("focus", () => syncEngine.auto("focus"));
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") {
        syncEngine.auto("visible");
      }
    });
    await swBridge.register();
    syncEngine.auto("startup");
  })().catch((error) => console.error("Init error", error));
});
