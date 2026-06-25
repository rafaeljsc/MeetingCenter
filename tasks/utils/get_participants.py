import logging

import requests

from tasks.utils.get_graph_data import get_graph_data

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_participants(call_id: str, invites: list[dict], session: requests.Session) -> list[dict]:
    """Retorna participantes de uma call.

    Args:
        call_id (str): Id do callRecord
        invites (list[dict]): Lista de convidados do evento
        session (requests.Session): Sessão do graph autenticada
    """

    output = []
    url = f"https://graph.microsoft.com/v1.0/communications/callRecords/{call_id}?$expand=participants_v2"
    participants = get_graph_data(url, session)

    for p in participants.get("participants_v2", []):
        user = p.get("identity", {}).get("user")

        if not user or not user.get("userPrincipalName") or user.get("id") == user.get("displayName"):
            continue

        name = user.get("displayName").title()
        mail = user.get("userPrincipalName").lower()

        if "#ext#" in mail:
            cache_mail = next(
                (i["mail"] for i in invites if i["name"] == name),
                None,
            )
            mail = cache_mail or mail

        output.append(
            {
                "name": name,
                "mail": mail,
                "company": mail.split("@" if "#ext#" not in mail else "_")[1].split(".")[0].title(),
            },
        )

    return output
