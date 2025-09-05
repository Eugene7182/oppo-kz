# Deploy на Render

## Backend

Build: `pip install -r requirements.txt`

Start: `export PYTHONPATH="$(pwd)" && alembic -c alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Frontend

Build: `npm ci --include=dev && npm run build`

Publish: `dist`
