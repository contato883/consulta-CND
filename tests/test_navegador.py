import pytest

from consulta_cnd.navegador import PORTAIS, consultar_cnpj_no_portal, detectar_situacao


def test_portais_conhecidos():
    assert "rfb" in PORTAIS
    assert "cndt" in PORTAIS
    assert "pr" in PORTAIS
    assert "ceuazul-pr" in PORTAIS
    assert PORTAIS["cndt"]["url"] == "https://cndt-certidao.tst.jus.br/"
    assert PORTAIS["pr"]["url"] == "https://cdwfazenda.paas.pr.gov.br/cdwportal/certidao/automatica"
    assert PORTAIS["ceuazul-pr"]["url"] == (
        "https://ceuazul.atende.net/autoatendimento/servicos/"
        "certidao-negativa-de-debitos/detalhar/1"
    )


def test_consultar_cnpj_no_portal_rejeita_portal_desconhecido(tmp_path):
    with pytest.raises(ValueError):
        consultar_cnpj_no_portal(None, "11.222.333/0001-81", tmp_path, portal="portal-inexistente")


def test_detectar_situacao_negativa():
    texto = "<p>Foi emitida a CERTIDÃO NEGATIVA de débitos relativos...</p>"
    assert detectar_situacao(texto) == "NEGATIVA"


def test_detectar_situacao_positiva_com_efeito_de_negativa():
    texto = "<p>CERTIDÃO POSITIVA COM EFEITO DE NEGATIVA de débitos...</p>"
    assert detectar_situacao(texto) == "POSITIVA_COM_EFEITO_DE_NEGATIVA"


def test_detectar_situacao_positiva():
    texto = "<p>CERTIDÃO POSITIVA de débitos relativos a créditos tributários...</p>"
    assert detectar_situacao(texto) == "POSITIVA"


def test_detectar_situacao_desconhecida_retorna_none():
    assert detectar_situacao("<p>página de erro qualquer</p>") is None
