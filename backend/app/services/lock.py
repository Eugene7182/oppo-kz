from contextlib import asynccontextmanager
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

@asynccontextmanager
async def advisory_lock(session: AsyncSession, key: int) -> AsyncIterator[bool]:
    got = False
    try:
        res = await session.execute(text("SELECT pg_try_advisory_lock(:k)"), {"k": key})
        got = bool(res.scalar())
        yield got
    finally:
        if got:
            await session.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": key})
