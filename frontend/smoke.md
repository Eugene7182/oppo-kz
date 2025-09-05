# Smoke test

- Открыть `/login`, войти админом → редирект на `/health`. **OK/FAIL**
- На `/health` все 3 карточки зелёные (health/version/db_status). **OK/FAIL**
- Открыть `/dicts/networks`: создать сеть, увидеть в таблице, переименовать, удалить. **OK/FAIL**
- Открыть `/price/upload`: загрузить `price.csv` с 3 строками → увидеть job в `/imports/jobs` → статус done. **OK/FAIL**
- Открыть `/inventory/balances`: фильтры работают; на `/inventory/adjust` изменить остаток — баланс обновился. **OK/FAIL**
- Открыть `/moves`: создать перемещение в одной сети/регионе → approve → остатки изменились. **OK/FAIL**
- Открыть `/sales/network` и `/sales/promoters`: загрузить CSV, выполнить `/sales/reconcile`, увидеть статусы. **OK/FAIL**
- `/messages`: создать in-app, увидеть в списке; email — показать toast `sent/logged`. **OK/FAIL**
- `/flags`: создать и переключить флаг. **OK/FAIL**
- Проверить, что при истёкшем токене UI автоматически обновляет токен и повторяет запрос. **OK/FAIL**
