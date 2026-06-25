import logging

import requests

from tasks.utils.get_invites import get_invites
from tasks.utils.get_participants import get_participants
from tasks.utils.min_max_call_dates import min_max_call_dates
from tasks.utils.validate_calls import validate_calls

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def call_filter(raw_calls: list[dict], g_session: requests.Session) -> list[dict]:
    """Filtragem para retornar somente as calls agendadas que possuam transcripts.

    Args:
        raw_calls (list[dict]): Lista de CallRecords
        g_session (requests.Session): Sessão autenticada da conexão do Graph
    """

    calls_per_user = validate_calls(raw_calls)
    if not calls_per_user:
        return []

    count_calls = 0
    count_users = 0
    count_transcripts = 0
    calls_total = sum([len(v["calls"]) for k, v in calls_per_user.items()])
    users_total = len(calls_per_user)
    min_date, max_date = min_max_call_dates(calls_per_user)
    relevant_calls = []

    for user_id, calls in calls_per_user.items():
        count_calls += len(calls["calls"])
        count_users += 1
        logger.info(
            f"users: {count_users}/{users_total}, calls: {count_calls}/{calls_total}, transcripts: {count_transcripts}",  # noqa: G004
        )

        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings/getAllTranscripts(meetingOrganizerUserId='{user_id}', startDateTime={min_date}, endDateTime={max_date})"
        meetings_with_transcript = g_session.get(url)
        if not meetings_with_transcript.ok or not meetings_with_transcript.json().get("value"):
            continue

        meetings_with_transcript = meetings_with_transcript.json()

        meetings_with_transcript_unique = []
        for meeting in meetings_with_transcript["value"]:
            cache = next(
                (i for i in meetings_with_transcript_unique if i.get("meetingId") == meeting["meetingId"]),
                None,
            )

            if cache:
                cache["transcripts_urls"].append(meeting["transcriptContentUrl"])
            else:
                transcript_url = meeting["transcriptContentUrl"]
                del meeting["transcriptContentUrl"]
                meeting["transcripts_urls"] = [transcript_url]
                meetings_with_transcript_unique.append(meeting)

        tmp_meetings_data = []
        for meeting in meetings_with_transcript_unique:
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings/{meeting['meetingId']}?$select=subject,participants,iCalUid,meetingId,chatInfo"
            meeting_details = g_session.get(url).json()

            for call in calls["calls"]:
                url = f"https://graph.microsoft.com/v1.0/users/{user_id}/onlineMeetings/{meeting['meetingId']}/transcripts?$filter=callId eq '{call['id']}'"
                transcripts_with_call_id = g_session.get(url).json()
                if not transcripts_with_call_id.get("value"):
                    continue

                tmp_meetings_data.append(
                    {
                        "user_id": user_id,
                        "call_id": call["id"],
                        "transcripts_url": meeting["transcripts_urls"],
                        "subject": meeting_details.get("subject"),
                        "ical_uid": meeting_details.get("iCalUid"),
                        "aux_participants": [
                            i.get("identity", {}).get("user", {}).get("id")
                            for i in meeting_details.get("participants", {}).get("attendees")
                        ],
                    },
                )

        if not tmp_meetings_data:
            continue

        for data in tmp_meetings_data:
            invites = get_invites(data, g_session)

            participants = get_participants(
                call_id=data["call_id"],
                invites=invites,
                session=g_session,
            )

            call_details = next(
                (i for i in raw_calls if i["id"] == data["call_id"]),
                None,
            )

            if not invites or not participants or not call_details:
                continue

            user = (
                call_details.get("organizer_v2", {}).get("identity", {}).get("user")
            )

            call_data = {
                "call_id": data["call_id"],
                "transcripts_url": data["transcripts_url"],
                "call_title": data["subject"],
                "start_date": call_details["startDateTime"],
                "end_date": call_details["endDateTime"],
                "organizer": f"{user.get('displayName')} ({user.get('userPrincipalName')})",
                "organizer_id": user.get("id"),
                "companies": list(set(i["company"] for i in participants)),  # noqa: C401
                "invites": invites,
                "participants": participants,
            }

            relevant_calls.append(call_data)
            count_transcripts += 1

    return relevant_calls
