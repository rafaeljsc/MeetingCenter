import re
from time import sleep

import requests

from tasks.utils.auth import Tokens


def download_transcripts(transcript_url: str, g_session: requests.Session) -> str | None:
    g_session.headers.update({"Accept": "text/vtt"})

    while True:
        result = g_session.get(transcript_url)
        if result.status_code == 401:
            sleep(1)
            g_session.headers.update(Tokens().graph())
            g_session.headers.update({"Accept": "text/vtt"})

        elif not str(result.status_code).startswith("2"):
            return None

        else:
            result.encoding = "utf-8"
            g_session.headers.update({"Accept": "application/json"})
            return result.text


def parse_vtt(vtt_text: str) -> list[dict]:
    """Extrai falas do VTT para lista de dicts."""
    vtt_pattern = re.compile(
        r"<v\s(?P<speaker>[^>]+)>(?P<text>.*?)</v>",
        re.DOTALL,
    )

    records = []
    for match in vtt_pattern.finditer(vtt_text):
        if len(str(match.group("text")).split()) < 3:
            continue

        records.append(
            {
                match.group("speaker").strip().title(): match.group("text").strip(),
            },
        )

    return records


def group_consecutive_speakers(transcript_json: list[dict]) -> list[dict]:
    """Agrupa falas consecutivas do mesmo speaker."""

    light_transcript = []
    for item in transcript_json:
        cache = light_transcript[-1] if light_transcript else None
        if cache and cache.keys() == item.keys():
            cache[next(iter(cache))] += " " + next(iter(item.values()))
        else:
            light_transcript.append(item)

    return light_transcript


def get_transcripts(transcripts_url: list[str], g_session: requests.Session) -> list[dict]:
    final_transcript = []
    for transcript_url in transcripts_url:
        transcript = download_transcripts(
            transcript_url=transcript_url,
            g_session=g_session,
        )

        if not transcript:
            continue

        transcript_json = parse_vtt(transcript)
        light_transcript = group_consecutive_speakers(transcript_json)
        final_transcript.extend(light_transcript)

    return final_transcript
