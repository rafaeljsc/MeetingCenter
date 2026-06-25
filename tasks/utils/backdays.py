from datetime import UTC, datetime, timedelta


def backdays(days: int) -> tuple[str, str]:
    """Gera um intervalo de tempo em formato ISO 8601 (UTC) entre o início do dia atual
    e uma data passada, retrocedendo um número especificado de dias.

    Args:
        days (int): Número de dias para retroceder a partir do dia atual.
    """

    utc_now = datetime.now(UTC)
    end = datetime(utc_now.year, utc_now.month, utc_now.day, 0, 0, 0, tzinfo=UTC)
    start = end - timedelta(days=days)

    end_str = end.isoformat().replace("+00:00", "Z")
    start_str = start.isoformat().replace("+00:00", "Z")
    return start_str, end_str
