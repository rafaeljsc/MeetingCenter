import base64
import logging
import os
import time
from pathlib import Path

import jwt
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs12

logger = logging.getLogger(__name__)


class Tokens:
    def graph(self) -> dict[str, str]:
        """Retorna um dicionário com Bearer Token para requests na Graph API."""

        url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
        body = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("AZURE_CLIENT_ID"),
            "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
            "scope": "https://graph.microsoft.com/.default",
        }

        response = requests.post(url, data=body)  # noqa: S113
        response.raise_for_status()
        access_token = response.json()["access_token"]

        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def spo_token(self) -> dict[str, str]:
        """Retorna um dicionário com Bearer Token para requests na REST API do Sharepoint."""

        cert = Path(__file__).parent / "cert.pfx"

        if not cert.exists():
            msg = f"Certificate file 'cert.pfx' not found in {cert}."
            logger.error(msg)
            raise FileNotFoundError(msg)

        try:
            with cert.open("rb") as f:
                private_key, certificate, _ = pkcs12.load_key_and_certificates(f.read(), b"")

            # Calcula thumbprint SHA-1 (x5t)
            cert_der = certificate.public_bytes(serialization.Encoding.DER)
            digest = hashes.Hash(hashes.SHA1())  # noqa: S303
            digest.update(cert_der)
            thumbprint = digest.finalize().hex().upper()

            # Cabeçalho do JWT
            header = {
                "alg": "RS256",
                "typ": "JWT",
                "x5t": base64.urlsafe_b64encode(bytes.fromhex(thumbprint)).decode("utf-8").rstrip("="),
            }

            # Payload do JWT
            auth_url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
            payload = {
                "aud": auth_url,
                "exp": int(time.time()) + 3600,
                "iss": os.getenv("AZURE_CLIENT_ID"),
                "sub": os.getenv("AZURE_CLIENT_ID"),
                "jti": str(time.time()),
            }

            # Criação do JWT
            client_assertion = jwt.encode(payload, private_key, algorithm="RS256", headers=header)

            # Dados para o POST
            tenant_name = (
                requests.get("https://graph.microsoft.com/v1.0/sites/root", headers=self.graph())  # noqa: S113
                .json()["id"]
                .split(".")[0]
            )
            data = {
                "grant_type": "client_credentials",
                "client_id": os.getenv("AZURE_CLIENT_ID"),
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": client_assertion,
                "scope": f"https://{tenant_name}.sharepoint.com/.default",
            }

            # Post
            access_token_resp = requests.post(auth_url, data=data)  # noqa: S113
            access_token_resp.raise_for_status()
            token_json = access_token_resp.json()

            return {
                "Authorization": f"Bearer {token_json['access_token']}",
                "Accept": "application/json",
            }

        except Exception as e:
            error_msg = f"An error occurred while getting the token. {e}"
            logger.exception(error_msg)
            raise RuntimeError(error_msg) from e
