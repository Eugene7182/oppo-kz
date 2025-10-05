# Frontend (Vite + React + Tailwind + shadcn-style UI)

## Структура (FSD)

- `src/app` — роутинг, провайдеры, регистрация Service Worker.
- `src/entities` — доменные типы и моки (user, product, sale, plan, bonus, dict).
- `src/features` — бизнес-фичи (формы продаж, коррекции, синхронизация, bulk-планы и т.д.).
- `src/widgets` — виджеты (KpiCards, FilterBar, ResponsiveTable, ChartPlaceholder, StatusBanner, ModalSheet, ConflictDialog).
- `src/pages` — страницы по ролям: promoter, supervisor, office, admin/*.

## Установка и запуск

### Windows PowerShell
```powershell
cd frontend
npm install
$env:VITE_API_URL="http://localhost:8000"  # или оставить пустым для mock режима
npm run dev
```

### bash / zsh
```bash
cd frontend
npm install
export VITE_API_URL="http://localhost:8000" # пустое значение включает офлайн-моки
npm run dev
```

## Сборка (Render static)

```bash
npm run build
```

Результат в `frontend/dist`. На Render используем build-команду `npm install && npm run build`.

## Offline-first

- Service Worker: `public/sw.js` + регистрация в `src/app/service-worker/registerServiceWorker.ts`.
- IndexedDB helper: `src/shared/lib/indexedDb.ts` хранит продажи, планы и outbox.
- Фича `SyncControl` отображает статус (онлайн/оффлайн/в очереди) и ручную кнопку «Синхронизировать».
- При сетевых ошибках axios добавляет запросы в outbox с Idempotency-Key.
