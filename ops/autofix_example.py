"""
Пример "safe-autofix": ищем типовую ошибку в frontend/src/shared/api/http.ts
и гарантируем, что есть VITE_API_URL. Если нужно — правим файл и оставляем
комментарий. Никаких произвольных правок по проекту.
"""
from __future__ import annotations
from pathlib import Path

TARGET = Path("frontend/src/shared/api/http.ts")

def main():
    if not TARGET.exists():
        print("skip: file not found"); return 0
    text = TARGET.read_text(encoding="utf-8")
    if "VITE_API_URL" in text:
        print("ok: VITE_API_URL already used"); return 0
    # минимально инвазивная правка: добавим альтернативу
    new = text.replace('const BASE = ', 'const BASE = import.meta.env.VITE_API_URL || ') \
              if 'const BASE = ' in text else \
              f'const BASE = import.meta.env.VITE_API_URL || "";\n{text}'
    TARGET.write_text(new, encoding="utf-8")
    print("patched: added VITE_API_URL fallback")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
