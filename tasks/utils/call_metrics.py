import logging
import traceback as tb
from datetime import datetime
from typing import Any

import pytz

logger = logging.getLogger("transcript_organizer")


def call_metrics(call: dict) -> dict[str, Any] | None:
    """Complementa a ata com detalhes e métricas a respeito da reunião.

    Args:
        call (dict): Objeto callRecord
    """

    try:
        utc = pytz.utc
        americas_tz = pytz.timezone("America/Sao_Paulo")
        call_start_date = utc.localize(
            datetime.strptime(call["start_date"][:19], "%Y-%m-%dT%H:%M:%S"),  # noqa: DTZ007
        ).astimezone(americas_tz)
        call_end_date = utc.localize(
            datetime.strptime(call["end_date"][:19], "%Y-%m-%dT%H:%M:%S"),  # noqa: DTZ007
        ).astimezone(americas_tz)

        diff = call_end_date - call_start_date
        call_duration_min = int(diff.total_seconds() / 60)

        call_key_attr = {
            "start_date": call_start_date.isoformat(),
            "end_date": call_end_date.isoformat(),
            "call_duration_min": call_duration_min,
        }

    except Exception:
        logger.exception("Erro ao processar atributos da call")
        logger.exception(str(tb.format_exc()))

    else:
        return call_key_attr
