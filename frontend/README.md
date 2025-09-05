# Frontend

## Установка

### Windows PowerShell
```powershell
cd frontend
npm i
$env:VITE_API_URL="http://localhost:8000"
npm run dev
```

### bash
```bash
cd frontend
npm i
export VITE_API_URL="http://localhost:8000"
npm run dev
```

## Сборка

```bash
npm run build
```
Готовая сборка появится в папке `dist/` (Render Static Site: `frontend/dist`).
