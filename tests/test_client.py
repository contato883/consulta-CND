from unittest.mock import MagicMock, patch

import pytest

from consulta_cnd.auth import SerproAuth
from consulta_cnd.client import ConsultaCndClient, ConsultaCndError

CNPJ_FICTICIO_VALIDO = "11.222.333/0001-81"


def _client_com_token_mockado() -> ConsultaCndClient:
    auth = MagicMock(spec=SerproAuth)
    auth.get_token.return_value = "token-falso"
    return ConsultaCndClient(auth)


def test_consultar_rejeita_cnpj_invalido():
    client = _client_com_token_mockado()
    with pytest.raises(ConsultaCndError):
        client.consultar("11.222.333/0001-80")


def test_consultar_retorna_resultado_para_certidao_negativa():
    client = _client_com_token_mockado()
    resposta = MagicMock(status_code=200)
    resposta.json.return_value = {
        "situacao": "negativa",
        "numeroCertidao": "12345",
        "dataEmissao": "2026-09-01",
        "dataValidade": "2027-03-01",
    }

    with patch("consulta_cnd.client.requests.post", return_value=resposta):
        resultado = client.consultar(CNPJ_FICTICIO_VALIDO)

    assert resultado.situacao == "NEGATIVA"
    assert resultado.regular
    assert resultado.numero_certidao == "12345"


def test_consultar_levanta_erro_em_http_diferente_de_200():
    client = _client_com_token_mockado()
    resposta = MagicMock(status_code=500, text="erro interno")

    with patch("consulta_cnd.client.requests.post", return_value=resposta):
        with pytest.raises(ConsultaCndError):
            client.consultar(CNPJ_FICTICIO_VALIDO)


def test_consultar_marca_positiva_como_nao_regular():
    client = _client_com_token_mockado()
    resposta = MagicMock(status_code=200)
    resposta.json.return_value = {"situacao": "positiva"}

    with patch("consulta_cnd.client.requests.post", return_value=resposta):
        resultado = client.consultar(CNPJ_FICTICIO_VALIDO)

    assert not resultado.regular
