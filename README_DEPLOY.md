OPPO KZ — Release Build (generated 2025-08-31 20:22:10)

Главные новшества:
- PWA Web Push (VAPID) — фото-напоминания только для супервизоров, если админ включил ENABLE_PHOTO_REMINDERS.
- Гео/селфи — реализовано, отключено фичефлагами (можно включить позже).
- Бонусы: перевыполнение плана и проекция — готовые сервисы.
- «Запрос товара» от промоутера → уведомления супервизору.
- Ежемесячный отчёт (CSV) — скелет.
- «Средний чек» убран из метрик/примеров.

## Render ENV
- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- JWT_SECRET
- ADMIN_EMAIL
- ADMIN_PASSWORD
- ADMIN_NAME  # на первый старт

Настройки ENV (Render → Backend):
  ENABLE_GEO_CHECKIN=false
  ENABLE_SELFIE_CHECKIN=false
  ENABLE_AI_INSIGHTS=true
  ENABLE_PHOTO_REMINDERS=true   # включит фото-напоминания по расписанию
  TIMEZONE=Asia/Almaty
  VAPID_PUBLIC_KEY=...         # можно не задавать — сгенерируется и сохранится в БД
  VAPID_PRIVATE_KEY=...
  VAPID_SUBJECT=mailto:you@example.com

Подключение роутеров (если не подключены автоматически):
  app/api/v1/api.py → include feature_flags, notifications, stock_requests, reports, push

Планировщик:
  app/main.py →
    from app.services.scheduler import start_scheduler
    @app.on_event("startup")
    async def _start_scheduler():
        await start_scheduler(app)

Frontend:
  public/manifest.json, public/service-worker.js присутствуют.
  Settings → Notifications: кнопка «Включить и отправить тест».


## Скрипты /scripts
- `scripts/smoke.sh` — E2E smoke-тест API (curl + python). Пример:
  ```bash
  BASE_URL=https://oppo-api.onrender.com   ADMIN_USER=admin@oppo.kz ADMIN_PASS=StrongPass123   ./scripts/smoke.sh
  ```
- `scripts/migrate.sh` — Alembic upgrade head.
- `scripts/curl_tokens.sh` — получить токен админа (raw JSON).
- `scripts/oppo_kz_postman.json` — коллекция Postman.
- `Makefile` — удобные цели: `make dev-up|dev-down|migrate|smoke`.


## Дополнительные скрипты
- `scripts/seed_demo.sh` — засеять демо-данные через API (инвайт/регистрация промоутера, store-coeff если есть store, проверка feature-flags).
  ```bash
  BASE_URL=http://localhost:8000 ADMIN_USER=admin@oppo.kz ADMIN_PASS=StrongPass123 ./scripts/seed_demo.sh
  ```
- `scripts/e2e_ai_stock_reports.sh` — пройтись по AI/Stock/Reports эндпойнтам и вывести статусы.
  ```bash
  BASE_URL=https://<backend-domain> ADMIN_USER=<user> ADMIN_PASS=<pass> ./scripts/e2e_ai_stock_reports.sh
  ```


## Полный сид (демо-данные под AI/Stock/Reports/Sales)
- `scripts/seed_full.sh` — создаёт Stores, SKUs, PriceList, начальные остатки, продажи, отгрузки/в пути, бонусную сетку и коэффициенты.
  Скрипт **робастный**: для каждого домена пробует несколько вариантов эндпойнтов и пропускает те, которых нет.
  ```bash
  BASE_URL=http://localhost:8000   ADMIN_USER=admin@oppo.kz ADMIN_PASS=StrongPass123   ./scripts/seed_full.sh
  ```
  После этого `scripts/e2e_ai_stock_reports.sh` и фронтенд отчёты будут иметь данные.


## Очистка и нагрузочное наполнение
- `scripts/wipe_demo.sh` — удаляет только демо-данные, созданные сидерами (по умолчанию DRY-RUN).  
  Запуск:
  ```bash
  # посмотреть, что будет удалено (по умолчанию dry-run)
  BASE_URL=http://localhost:8000 ADMIN_USER=admin@oppo.kz ADMIN_PASS=StrongPass123 ./scripts/wipe_demo.sh
  # реально удалить
  CONFIRM=YES DRY_RUN=false BASE_URL=... ADMIN_USER=... ADMIN_PASS=... ./scripts/wipe_demo.sh
  ```

- `scripts/seed_sales_bulk.sh` — массовая генерация продаж для графиков/нагрузки.  
  Параметры: `DAYS`, `PER_DAY`, `STORES`, `SKUS`, `PROMOTER`. Пытается `/api/v1/sales/bulk`, иначе постит поштучно.
  ```bash
  DAYS=14 PER_DAY=200 STORES=A01,A02 SKUS=OPPO-A1K,OPPO-RENO10 ./scripts/seed_sales_bulk.sh
  ```

### Makefile шорткаты
```bash
make wipe CONFIRM=YES DRY_RUN=false        # стереть демо-данные
make seed-full                              # полный сид (всё доменное)
make load-sales DAYS=30 PER_DAY=100         # массовые продажи
```


## Новые фичи (эндпойнты)
- **Импорт CSV**: `POST /api/v1/imports/{kind}` (csv), возвращает `{rows, sample}`.
- **Экспорт шаблона CSV**: `GET /api/v1/exports/templates/{kind}.csv`.
- **Бонусы**: `POST /api/v1/bonus/calc-preview`, `POST /api/v1/bonus/calc-commit` (создаёт записи в `bonus_payouts`).
- **Трансферы (эвристика)**: `GET /api/v1/transfers/suggest?store=A01&horizon=14&safety=7`.
- **WebSocket**: `GET /api/v1/ws` (ws), эхо/бродкаст.
- **Аудит**: `GET /api/v1/audit` (role: super).
- **Кампании**: `GET/POST /api/v1/campaigns`.
- **Sentry**: включается через `SENTRY_DSN`.
- **CI**: `.github/workflows/ci.yml`.
