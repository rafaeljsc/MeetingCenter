from __future__ import annotations

import os
from typing import Final

# ---------------------------------------------------------------------------
# Valores reconhecidos como "true" (substituindo gamabot_core.utils.constants)
# ---------------------------------------------------------------------------
TRUE_VALUES: Final[frozenset[str]] = frozenset({"true", "1", "yes", "on"})

# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------
PORTAL_REUNIOES_PROCESSING_ENABLED: Final[bool] = (
    os.getenv("PORTAL_REUNIOES_PROCESSING_ENABLED", "true").lower() in TRUE_VALUES
)
"""Ativa o modo de processamento do Portal Reuniões."""

DEBUG_ENABLED: Final[bool] = os.getenv("DEBUG", "false").lower() in TRUE_VALUES
"""Ativa o modo de depuração da aplicação."""

# ---------------------------------------------------------------------------
# Redis
# ---------------------------------------------------------------------------
REDIS_URL: Final[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")
"""URL de conexão com o Redis."""

# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
DATABASE_URL: Final[str] = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://impar:localhost@localhost:5432/gamabot",
)
"""String de conexão assíncrona com o PostgreSQL (asyncpg)."""

# ---------------------------------------------------------------------------
# Azure AD / Graph
# ---------------------------------------------------------------------------
AZURE_TENANT_ID: Final[str | None] = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID: Final[str | None] = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET: Final[str | None] = os.getenv("AZURE_CLIENT_SECRET")

# ---------------------------------------------------------------------------
# Azure OpenAI
# ---------------------------------------------------------------------------
AZURE_OPENAI_ENDPOINT: Final[str] = os.getenv(
    "AZURE_OPENAI_ENDPOINT", "https://sek-openai.openai.azure.com/"
)
AZURE_GPT_PREMIUM_DEPLOYMENT_NAME: Final[str] = os.getenv(
    "AZURE_GPT_PREMIUM_DEPLOYMENT_NAME", "gpt-4o"
)
AZURE_GPT_LOWCOST_DEPLOYMENT_NAME: Final[str] = os.getenv(
    "AZURE_GPT_LOWCOST_DEPLOYMENT_NAME", "gpt-4o-mini"
)
AZURE_OPENAI_API_VERSION: Final[str] = os.getenv(
    "AZURE_OPENAI_API_VERSION", "2023-05-15"
)
LLM_TEMPERATURE: Final[float] = 0.2
DEFAULT_LLM_MAX_TOKENS: Final[int] = 2000
