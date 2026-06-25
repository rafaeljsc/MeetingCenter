import logging

import requests

from tasks.utils.get_graph_data import get_graph_data

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def aux_participants(meeting_data: dict, r_session: requests.Session) -> list[dict]:
    """Tenta retornar dados dos participantes pelo upn interno.

    Args:
        meeting_data (dict): Dados da meeting
        r_session (requests.Session): Sessão do graph autenticada
    """

    aux_invites = []
    for user in meeting_data["aux_participants"]:
        url = f"https://graph.microsoft.com/v1.0/users/{user}"
        result = r_session.get(url)

        if result.status_code != 200:
            continue

        aux_user = result.json()

        aux_invites.append(
            {
                "name": aux_user.get("displayName", "").title(),
                "mail": aux_user.get("mail", "").lower(),
                "company": aux_user.get("mail", "").split("@")[1].split(".")[0].title(),
            },
        )

    return aux_invites


def get_invites(meeting_data: dict, r_session: requests.Session) -> list[dict] | None:
    """Retorna convidados de um evento.

    Args:
        meeting_data (dict): Dados da meeting
        r_session (requests.Session): Sessão do graph autenticada
    """

    invites = []

    if meeting_data.get("ical_uid"):
        url = f"https://graph.microsoft.com/v1.0/users/{meeting_data['user_id']}/events?$filter=iCalUId eq '{meeting_data['ical_uid']}'"
        event = get_graph_data(url, r_session)

        if event:
            event = event[0]
            aux = [
                {
                    "name": i.get("emailAddress", {}).get("name", "").title(),
                    "mail": i.get("emailAddress", {}).get("address", "").lower(),
                    "company": i.get("emailAddress", {}).get("address", "").split("@")[1].split(".")[0].title(),
                }
                for i in event.get("attendees")
            ]
            invites.extend(aux)

        else:
            invites.extend(aux_participants(meeting_data, r_session))

    else:
        invites.extend(aux_participants(meeting_data, r_session))

    return invites
