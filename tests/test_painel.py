import json

from consulta_cnd.painel import _status_celula, gerar_painel_html


def test_status_celula_none_e_pendente():
    texto, classe = _status_celula(None)
    assert texto == "PENDENTE DE VERIFICAÇÃO"
    assert classe == "pendente"


def test_status_celula_regular():
    texto, classe = _status_celula("NEGATIVA")
    assert texto == "REGULAR"
    assert classe == "regular"


def test_status_celula_irregular_mostra_situacao_bruta():
    texto, classe = _status_celula("POSITIVA")
    assert texto == "PENDÊNCIA (POSITIVA)"
    assert classe == "irregular"


def _csv_ficticio(tmp_path):
    caminho = tmp_path / "clientes.csv"
    caminho.write_text(
        "cnpj,razao_social,municipio,uf\n"
        "11.222.333/0001-81,Zebra Fictícia LTDA,CEU AZUL,PR\n"
        "40.734.037/0001-68,Alfa Fictícia LTDA,MUNICIPIO SEM PORTAL,PR\n"
    )
    return caminho


def test_gerar_painel_html_ordena_alfabeticamente_e_marca_pendente(tmp_path):
    caminho = _csv_ficticio(tmp_path)

    saida = gerar_painel_html(caminho)

    assert saida.index("Alfa Fictícia LTDA") < saida.index("Zebra Fictícia LTDA")
    assert "PENDENTE DE VERIFICAÇÃO" in saida
    assert "SEM PORTAL CADASTRADO" in saida


def test_gerar_painel_html_usa_resultados_reais(tmp_path):
    caminho = _csv_ficticio(tmp_path)
    resultados = tmp_path / "resultados.json"
    resultados.write_text(
        json.dumps({"11222333000181": {"rfb": "NEGATIVA", "cndt": "POSITIVA"}}),
        encoding="utf-8",
    )

    saida = gerar_painel_html(caminho, caminho_resultados=resultados)

    assert "REGULAR" in saida
    assert "PENDÊNCIA (POSITIVA)" in saida
