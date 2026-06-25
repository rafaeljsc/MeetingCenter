from datetime import datetime


def min_max_call_dates(calls: dict) -> tuple[str, str]:
    """Retorna a menor e a maior data das calls. Utilizado para o filtro de meetings.

    Args:
        calls (dict): callRecord agrupadas
    """

    min_date = min(
        [datetime.fromisoformat(item["start_date"]) for k, v in calls.items() for item in v["calls"]],
    )

    max_date = max(
        [datetime.fromisoformat(item["end_date"]) for k, v in calls.items() for item in v["calls"]],
    )

    return min_date.isoformat()[:19] + "Z", max_date.isoformat()[:19] + "Z"
