import base64
import logging
import traceback as tb

import requests

from tasks.utils.auth import Tokens

logger = logging.getLogger("gerador_atas_send_mail_graph")


def sendmail_graph(
    g_session: requests.Session,
    subject: str,
    to: list[str],
    sender: str,
    content: str,
    attachment_file: str | None = None,
    mime_type: str | None = None,
) -> requests.Response:
    """Envia e-mail pelo Graph.

    Args:
        g_session (requests.Session): Sessão autenticada da conexão do Graph
        subject (str): Assunto do e-mail
        to (list[str]): Lista dos endereços de e-mail dos destinatários
        sender (str): Endereço de e-mail do remetente ou caixa compartilhada
        content (str): Corpo do e-mail
        attachment_file (str): Caminho do anexo
        mime_type (str): mime_type do anexo
    """

    try:
        to_recipients = [{"emailAddress": {"address": address}} for address in to]

        email_msg = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": content,
                },
                "toRecipients": to_recipients,
            },
        }

        if attachment_file is not None:
            with open(attachment_file, "rb") as f:  # noqa: PTH123
                file_content = f.read()

            encoded_content = base64.b64encode(file_content).decode("utf-8")

            email_msg["message"]["attachments"] = [
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": str(attachment_file),
                    "contentBytes": encoded_content,
                    "contentType": mime_type,
                },
            ]

        send_url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
        while True:
            response = g_session.post(send_url, json=email_msg)
            if response.status_code != 401:
                break

            g_session = requests.Session()
            g_session.headers.update(Tokens().graph())
            continue

        if str(response.status_code).startswith("2"):
            return response

        raise Exception(f"Falha ao enviar email ({response.status_code}).")  # noqa: EM102, TRY002, TRY003, TRY301

    except Exception as e:
        logger.exception(f"Cannot send mail: {e}")  # noqa: G004, TRY401
        logger.exception(str(tb.format_exc()))
        return response
