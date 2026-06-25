import logging
from datetime import UTC, datetime

import requests
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import PORTAL_REUNIOES_PROCESSING_ENABLED
from db.connection import get_engine
from db.models.portal_reunioes import PortalReunioes
from tasks.utils.auth import Tokens
from tasks.utils.call_filter import call_filter
from tasks.utils.call_metrics import call_metrics
from tasks.utils.call_summary import call_summary
from tasks.utils.db_calls import db_calls
from tasks.utils.get_graph_data import get_graph_data
from tasks.utils.get_transcripts import get_transcripts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("PortalReunioesTask")

# Tipo do contexto SAQ (dict simples)
Context = dict


def _get_graph_session() -> requests.Session:
    """Cria e retorna uma sessão autenticada para a Graph API (lazy init)."""
    session = requests.Session()
    session.headers.update(Tokens().graph())
    return session


async def process_transcripts(calls: list[dict], g_session: requests.Session) -> None:
    """Retorna transcripts, transforma em json e salva no db.

    Args:
        calls (list[dict]): Lista de calls retornadas por `get_calls_with_transcript`
        g_session: sessão autenticada para a Graph API
    """

    calls_count = 0
    calls_total = len(calls)
    engine = get_engine()

    for call in calls:
        calls_count += 1
        logger.info(f"{calls_count}/{calls_total} transcripts processados")  # noqa: G004

        try:
            transcript = get_transcripts(
                transcripts_url=call["transcripts_url"],
                g_session=g_session,
            )

            transcript.insert(0, {"participants": call["participants"]})
            summary = call_summary(transcript)
        except Exception as e:
            logger.exception(
                {
                    "error": "Falha ao gerar a ata",
                    "details": str(e),
                    "current": call,
                }
            )
            continue

        if not summary or not summary.get("topics") or not summary.get("tasks"):
            logger.info(f"Dados insuficientes para gerar a ata. `call_id`: {call['call_id']}")  # noqa: G004
            continue

        del transcript[0]

        metrics = call_metrics(call)
        logger.info(f"current_call: {call}")  # noqa: G004

        logger.info("Enviando dados para o db")
        async with AsyncSession(engine) as session:
            try:
                current_date = datetime.now()  # noqa: DTZ005
                await session.execute(
                    insert(PortalReunioes).values(
                        call_id=call["call_id"],
                        call_title=call["call_title"],
                        start_date=metrics["start_date"],
                        end_date=metrics["end_date"],
                        call_duration_min=metrics["call_duration_min"],
                        organizer=call["organizer"],
                        participants_count=len(call["participants"]),
                        participants_name=[i["name"] for i in call["participants"]],
                        participants_mail=[i["mail"] for i in call["participants"]],
                        invites_count=len(call["invites"]),
                        invites_name=[i["name"] for i in call["invites"]],
                        invites_mail=[i["mail"] for i in call["invites"]],
                        companies=call["companies"],
                        goal=summary["goal"],
                        topics=summary["topics"],
                        tasks=summary["tasks"],
                        raw_transcript=transcript,
                        created_at=current_date,
                        updated_at=current_date,
                    ),
                )
                await session.commit()
            except Exception as e:
                logger.exception(f"Falha ao inserir registro no banco: {e}")  # noqa: G004


async def get_calls_with_transcript(g_session: requests.Session) -> list[dict] | None:
    """Retorna calls do dia atual e retém apenas aquelas com transcript."""

    start_range_str = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()[:19] + "Z"

    logger.info(f"Retornando calls de {start_range_str}")  # noqa: G004
    endpoint = f"https://graph.microsoft.com/v1.0/communications/callRecords?$filter=startDateTime ge {start_range_str}"
    raw_calls = get_graph_data(endpoint, g_session)

    if not raw_calls:
        logger.info("Não foram encontradas calls para o período identificado")
        return None

    if type(raw_calls) is requests.Response:
        logger.info({"error": "raw_calls", "return": raw_calls.json()})
        return None

    engine = get_engine()
    async with AsyncSession(engine) as session:
        calls_on_db = await db_calls(session)

    calls = [i for i in raw_calls if i["id"] not in calls_on_db]
    logger.info(f"{len(calls)} calls encontradas. Filtrando calls com transcript")  # noqa: G004

    calls_with_transcript = call_filter(
        raw_calls=calls,
        g_session=g_session,
    )
    return calls_with_transcript  # noqa: RET504


async def batch_call_transcript(ctx: Context) -> None:
    """Ponto de entrada para o processamento das reuniões (chamado pelo worker SAQ)."""
    if not PORTAL_REUNIOES_PROCESSING_ENABLED:
        logger.warning(
            "PROCESSAMENTO DESATIVADO — pulando ciclo para evitar consumo excessivo durante desenvolvimento",
        )
        return

    g_session = _get_graph_session()

    calls = await get_calls_with_transcript(g_session)
    if not calls:
        logger.info("Não foram encontradas reuniões com transcrição disponível no período especificado")
        return

    await process_transcripts(calls, g_session)
