from datetime import datetime
from zoneinfo import ZoneInfo

from db.models.portal_reunioes import PortalReunioes
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def db_calls(session: AsyncSession) -> set[str]:
    """Retorna um conjunto (set) dos ids das calls armazenadas no banco no dia atual."""

    today_start = datetime.now(tz=ZoneInfo("America/Sao_Paulo")).replace(hour=0, minute=0, second=0, microsecond=0)
    stmt = select(PortalReunioes.call_id).where(PortalReunioes.start_date >= today_start)
    result = await session.execute(stmt)
    ids = result.scalars().all()

    return set(ids)
