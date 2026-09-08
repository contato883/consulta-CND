"""Autenticação OAuth2 (client credentials) na plataforma de APIs do SERPRO."""

from __future__ import annotations

import time

import requests

TOKEN_URL = "https://gateway.apiserpro.serpro.gov.br/token"

# Margem de segurança para renovar o token antes do vencimento real.
_MARGEM_EXPIRACAO_SEGUNDOS = 30


class SerproAuthError(RuntimeError):
    """Falha ao obter ou renovar o token de acesso do SERPRO."""


class SerproAuth:
    """Obtém e mantém em cache o bearer token da plataforma SERPRO."""

    def __init__(self, consumer_key: str, consumer_secret: str, token_url: str = TOKEN_URL):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._token_url = token_url
        self._access_token: str | None = None
        self._expira_em: float = 0.0

    def get_token(self) -> str:
        if self._access_token and time.monotonic() < self._expira_em:
            return self._access_token

        resposta = requests.post(
            self._token_url,
            auth=(self._consumer_key, self._consumer_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"},
            timeout=15,
        )
        if resposta.status_code != 200:
            raise SerproAuthError(
                f"Falha ao obter token SERPRO (HTTP {resposta.status_code}): {resposta.text}"
            )

        dados = resposta.json()
        token = dados.get("access_token")
        if not token:
            raise SerproAuthError(f"Resposta de token sem access_token: {dados}")

        expira_em_segundos = float(dados.get("expires_in", 3600))
        self._access_token = token
        self._expira_em = time.monotonic() + expira_em_segundos - _MARGEM_EXPIRACAO_SEGUNDOS
        return token
