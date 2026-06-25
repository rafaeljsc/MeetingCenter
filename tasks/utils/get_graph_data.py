import logging
import time

import requests

from tasks.utils.auth import Tokens

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_graph_data(endpoint: str, r_session: requests.Session) -> dict | requests.Response:
    """Output paginado do endpoint informado.

    Args:
        endpoint (str): endpoint Graph
        r_session (requests.sessions.Session): Sessão autenticada da conexão do Graph
    """

    all_items = []

    while True:
        result = r_session.get(endpoint)
        if result.status_code == 401:
            graph_headers = Tokens().graph()
            r_session.headers.update(graph_headers)
            continue

        if result.status_code == 429:
            wait = int(result.headers.get("Retry-After"))
            logger.info(f"Throttling. Aguardando {wait}s")  # noqa: G004
            time.sleep(wait)
            continue

        if not result.ok:
            return result

        data = result.json()

        if "value" not in data:
            return data

        value = data.get("value")
        all_items.extend(value)
        endpoint = data.get("@odata.nextLink")
        if not endpoint:
            break

    return all_items
