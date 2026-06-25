import logging

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_transcripts_v2(call: dict, g_session: requests.Session, s_session: requests.Session) -> list[dict]:
    """Retorna transcript de uma reunião utilizando a API do Sharepoint.

    Args:
        call (dict): callRecord tratada
        g_session (requests.Session): Sessão do Graph autenticada
        s_session (requests.Session): Sessão do Sharepoint autenticada
    """

    endpoint = f"https://graph.microsoft.com/v1.0/users/{call['organizer_id']}/drive/special/recordings"
    result = g_session.get(endpoint)
    if not result.ok:
        logger.error(f"Não foi possível retornar a pasta de gravação do usuário `{call['organizer_id']}`")  # noqa: G004
        return None

    result = result.json()
    spo_base_url = "/".join(result.get("webUrl", "").split("/")[:5])
    recording_path = "/".join(result.get("webUrl", "").split("/")[-2:])
    drive_id = result.get("parentReference", {}).get("driveId")

    if not all([spo_base_url, recording_path, drive_id]):
        logger.error(
            f"Informações básicas indisponíveis. `spo_base_url`: {spo_base_url}, "  # noqa: G004
            f"`recording_path`: {recording_path}, `drive_id`: {drive_id}",
        )
        return None

    endpoint = f"{spo_base_url}/_api/web/GetFolderByServerRelativePath(decodedUrl='{recording_path}')/Files"

    params = {
        "$filter": (
            f"substringof('.mp4', Name)"
            f" and TimeCreated ge datetime'{call['start_date']}'"
            f" and TimeCreated lt datetime'{call['end_date']}'"
        ),
        "$select": "Name, Title, ServerRelativeUrl, UniqueId, TimeCreated",
    }

    result = s_session.get(endpoint, params=params)
    if not result.ok:
        logger.error("Não foi possível encontrar mídia associada ao transcript")
        return None

    medias = [i for i in result.json()["value"] if i["Title"] == call["call_title"]]

    full_transcript = []
    for media in medias:
        endpoint = (
            f"{spo_base_url}/_api/v2.1/drives/{drive_id}/items/{media['UniqueId']}/versions/current/media/transcripts"
        )
        result = s_session.get(endpoint)
        if not result.ok:
            logger.error(f"Falha ao retornar transcript para {endpoint}")  # noqa: G004
            return None

        transcripts = result.json()["value"]
        for transcript in transcripts:
            transcript_endpoint = f"{endpoint}/{transcript['id']}/content?format=json"
            result = s_session.get(transcript_endpoint)
            if not result.ok:
                logger.error(f"Falha ao retornar json do transcript {transcript_endpoint}")  # noqa: G004
                return None

            transcript_data = result.json()

            light_transcript = []
            for transcript_chunk in transcript_data["entries"]:
                if len(transcript_chunk.get("text", "").split()) < 3:
                    continue

                aux = {
                    transcript_chunk.get("speakerDisplayName", ""): transcript_chunk.get("text", ""),
                }

                cache = light_transcript[-1] if light_transcript else None
                if cache and cache.keys() == aux.keys():
                    cache[transcript_chunk.get("speakerDisplayName")] += " " + transcript_chunk.get("text")
                else:
                    light_transcript.append(aux)

            full_transcript.extend(light_transcript)

    return full_transcript
