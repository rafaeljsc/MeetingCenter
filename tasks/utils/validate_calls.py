import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def validate_calls(calls: dict) -> dict:
    """Filtra as calls que possuem as propriedades chaves válidas.

    Args:
        calls (list[dict]): Objetos CallRecord
    """

    calls_per_user = {}

    for call in calls:
        if (
            call.get("type") != "groupCall"
            or not call.get("organizer", {}).get("user", {})
            or call.get("organizer", {}).get("user", {}).get("tenantId") != os.getenv("AZURE_TENANT_ID")
        ):
            continue

        user = call.get("organizer", {}).get("user", {}).get("id")
        cache = calls_per_user.get(user)

        aux = {
            "id": call["id"],
            "start_date": call["startDateTime"],
            "end_date": call["endDateTime"],
        }

        if cache:
            cache["calls"].append(aux)
        else:
            calls_per_user[user] = {"calls": [aux]}

    return calls_per_user
