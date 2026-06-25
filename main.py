"""Entry point do worker SAQ para o Portal Reuniões.

Uso:
    cd portal_reunioes
    python main.py

    # ou com uvloop para melhor performance:
    python -m saq tasks.job.batch_call_transcript --queue portal_reunioes

Variáveis de ambiente necessárias: veja .env.example
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Garante que o diretório do projeto esteja no sys.path,
# independente de onde o script é chamado.
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Carrega .env automaticamente se python-dotenv estiver instalado
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from saq import CronJob, Queue, Worker

from config.settings import REDIS_URL
from tasks.job import batch_call_transcript

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("portal_reunioes.worker")


async def main() -> None:
    logger.info(f"Conectando ao Redis: {REDIS_URL}")  # noqa: G004
    queue = Queue.from_url(REDIS_URL, name="portal_reunioes")

    worker = Worker(
        queue=queue,
        functions=[batch_call_transcript],
        cron_jobs=[
            CronJob(
                function=batch_call_transcript,
                cron="*/10 * * * *",  # a cada 10 minutos
                unique=True,
                timeout=9999,
            ),
        ],
        concurrency=1,
    )

    logger.info("Worker iniciado. Aguardando jobs...")
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
