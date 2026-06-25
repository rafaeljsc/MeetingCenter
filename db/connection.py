"""Configuração e engine assíncrona do banco de dados.

Substitui custom.db.connection + custom.settings.db sem depender de
litestar, gamabot_core ou qualquer outro pacote do projeto principal.
"""
from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

from config.settings import DATABASE_URL, DEBUG_ENABLED


def _json_serializer(obj: object) -> str:
    return json.dumps(obj, default=str)


def _json_deserializer(s: str | bytes) -> object:
    return json.loads(s)

_engine_instance: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """Retorna (ou cria) a instância singleton do AsyncEngine."""
    global _engine_instance  # noqa: PLW0603
    if _engine_instance is not None:
        return _engine_instance

    engine = create_async_engine(
        url=DATABASE_URL,
        future=True,
        json_serializer=_json_serializer,
        json_deserializer=_json_deserializer,
        echo=DEBUG_ENABLED,
        echo_pool="debug" if DEBUG_ENABLED else False,
        max_overflow=6,
        pool_size=4,
        pool_timeout=30,
        pool_recycle=300,
        pool_pre_ping=False,
        pool_use_lifo=True,
        poolclass=AsyncAdaptedQueuePool,
    )
    _engine_instance = engine
    return _engine_instance


def get_session() -> AsyncSession:
    """Retorna uma nova AsyncSession a partir do engine singleton."""
    return AsyncSession(get_engine(), expire_on_commit=False)
