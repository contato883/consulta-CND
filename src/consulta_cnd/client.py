"""Cliente da API oficial "Consulta CND" do SERPRO (RFB/PGFN)."""

from __future__ import annotations

from typing import Any

import requests

from .auth import SerproAuth
from .cnpj import cnpj_valido, limpar_cnpj
from .models import ResultadoCertidao

BASE_URL_TRIAL = "https://gateway.apiserpro.serpro.gov.br/consulta-cnd-trial"
BASE_URL_PRODUCAO = "https://gateway.apiserpro.serpro.gov.br/consulta-cnd"


class ConsultaCndError(RuntimeError):
    """Falha ao consultar a CND de um CNPJ."""


class ConsultaCndClient:
    """
    Cliente da API "Consulta CND" do SERPRO.

    [A VERIFICAR] Os nomes de campo usados em `_montar_payload` e
    `_interpretar_resposta` seguem a documentação pública da API, mas o
    schema completo (Swagger/OpenAPI) só é liberado no Client Area do SERPRO
    após a contratação. Confira o Swagger do contrato antes de usar em
    produção e ajuste estes dois métodos se os campos divergirem — o resto
    do projeto não precisa mudar.
    """

    def __init__(self, auth: SerproAuth, producao: bool = False, timeout: int = 20):
        self._auth = auth
        self._base_url = BASE_URL_PRODUCAO if producao else BASE_URL_TRIAL
        self._timeout = timeout

    def consultar(self, cnpj: str) -> ResultadoCertidao:
        numero = limpar_cnpj(cnpj)
        if not cnpj_valido(numero):
            raise ConsultaCndError(f"CNPJ inválido: {cnpj}")

        token = self._auth.get_token()
        resposta = requests.post(
            f"{self._base_url}/v1/certidao",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=self._montar_payload(numero),
            timeout=self._timeout,
        )
        if resposta.status_code != 200:
            raise ConsultaCndError(
                f"Falha na consulta do CNPJ {numero} (HTTP {resposta.status_code}): {resposta.text}"
            )

        return self._interpretar_resposta(numero, resposta.json())

    @staticmethod
    def _montar_payload(cnpj: str) -> dict[str, Any]:
        return {"contribuinte": {"tipo": "PJ", "numero": cnpj}}

    @staticmethod
    def _interpretar_resposta(cnpj: str, dados: dict[str, Any]) -> ResultadoCertidao:
        situacao = str(dados.get("situacao", "DESCONHECIDA")).upper()
        return ResultadoCertidao(
            cnpj=cnpj,
            situacao=situacao,
            numero_certidao=dados.get("numeroCertidao"),
            data_emissao=dados.get("dataEmissao"),
            data_validade=dados.get("dataValidade"),
            resposta_bruta=dados,
        )
