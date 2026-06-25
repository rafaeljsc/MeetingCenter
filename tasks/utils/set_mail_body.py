import os
from datetime import datetime
from pathlib import Path

import pytz


def set_mail_body(data: dict) -> str:
    utc = pytz.utc
    americas_tz = pytz.timezone("America/Sao_Paulo")
    hour = utc.localize(datetime.now()).astimezone(americas_tz).hour  # noqa: DTZ005
    greeting = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"

    call_duration = (
        f"{data['call_duration_min']}min"
        if data["call_duration_min"] / 60 <= 1
        else f"{int(data['call_duration_min'] / 60)}h{(data['call_duration_min'] % 60)}min"
    )

    mail_body_path = Path(__file__).parent / "mail_body.html"
    with mail_body_path.open(encoding="utf-8") as f:
        mail_body = f.read()

    mail_body = (
        mail_body.replace("__organizer__", data["organizer"].split()[0].title())
        .replace("__call_title__", data["call_title"])
        .replace("__greeting__", greeting)
        .replace("__date_call_day__", data["start_date"].strftime("%d/%m/%Y"))
        .replace("__date_call_start_hour__", data["start_date"].strftime("%H:%M"))
        .replace("__date_call_end_hour__", data["end_date"].strftime("%H:%M"))
        .replace("__call_duration__", call_duration)
        .replace("__companies__", ", ".join(data["companies"]))
        .replace("__invites__", str(data["invites_count"]))
        .replace("__participants__", str(data["participants_count"]))
        .replace("__objetivo__", data["goal"])
    )

    return mail_body  # noqa: RET504
