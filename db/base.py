"""Base declarativa SQLAlchemy para o projeto standalone portal_reunioes.

Substitui `litestar.contrib.sqlalchemy.base.UUIDAuditBase` sem depender do
framework Litestar. Usa `advanced_alchemy` (já presente no pyproject.toml do
repositório principal) para manter compatibilidade com as migrations existentes.
"""
from __future__ import annotations

from advanced_alchemy.base import UUIDAuditBase  # noqa: F401  (re-exportado)

__all__ = ["UUIDAuditBase"]
