from unittest.mock import MagicMock, patch

import pytest

from consulta_cnd.auth import SerproAuth, SerproAuthError


def _resposta_token(status_code=200, access_token="abc123", expires_in=3600, texto="erro"):
    resposta = MagicMock(status_code=status_code, text=texto)
    resposta.json.return_value = {"access_token": access_token, "expires_in": expires_in}
    return resposta


def test_get_token_retorna_access_token():
    auth = SerproAuth("chave", "segredo")
    with patch("consulta_cnd.auth.requests.post", return_value=_resposta_token()) as post_mock:
        token = auth.get_token()

    assert token == "abc123"
    post_mock.assert_called_once()


def test_get_token_reaproveita_cache_enquanto_valido():
    auth = SerproAuth("chave", "segredo")
    with patch("consulta_cnd.auth.requests.post", return_value=_resposta_token()) as post_mock:
        auth.get_token()
        auth.get_token()

    post_mock.assert_called_once()


def test_get_token_levanta_erro_em_http_diferente_de_200():
    auth = SerproAuth("chave", "segredo")
    resposta = _resposta_token(status_code=401, texto="unauthorized")
    with patch("consulta_cnd.auth.requests.post", return_value=resposta):
        with pytest.raises(SerproAuthError):
            auth.get_token()


def test_get_token_levanta_erro_sem_access_token():
    auth = SerproAuth("chave", "segredo")
    resposta = MagicMock(status_code=200)
    resposta.json.return_value = {"expires_in": 3600}
    with patch("consulta_cnd.auth.requests.post", return_value=resposta):
        with pytest.raises(SerproAuthError):
            auth.get_token()
