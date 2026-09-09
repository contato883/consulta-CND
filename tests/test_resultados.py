import json

from consulta_cnd.models import ResultadoCertidao
from consulta_cnd.resultados import registrar_resultados


def _resultado(cnpj, situacao, portal):
    return ResultadoCertidao(cnpj=cnpj, situacao=situacao, resposta_bruta={"portal": portal})


def test_registrar_resultados_cria_arquivo_novo(tmp_path):
    caminho = tmp_path / "resultados.json"
    resultados = [_resultado("11.222.333/0001-81", "NEGATIVA", "rfb")]

    registrar_resultados(caminho, resultados)

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    assert dados == {"11222333000181": {"rfb": "NEGATIVA"}}


def test_registrar_resultados_mescla_com_existente(tmp_path):
    caminho = tmp_path / "resultados.json"
    caminho.write_text(json.dumps({"11222333000181": {"rfb": "NEGATIVA"}}), encoding="utf-8")

    registrar_resultados(caminho, [_resultado("11.222.333/0001-81", "POSITIVA", "cndt")])

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    assert dados == {"11222333000181": {"rfb": "NEGATIVA", "cndt": "POSITIVA"}}


def test_registrar_resultados_sobrescreve_mesmo_cnpj_e_tipo(tmp_path):
    caminho = tmp_path / "resultados.json"
    caminho.write_text(json.dumps({"11222333000181": {"rfb": "NEGATIVA"}}), encoding="utf-8")

    registrar_resultados(caminho, [_resultado("11.222.333/0001-81", "POSITIVA", "rfb")])

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    assert dados == {"11222333000181": {"rfb": "POSITIVA"}}


def test_registrar_resultados_mapeia_portais_municipais_para_municipal(tmp_path):
    caminho = tmp_path / "resultados.json"

    registrar_resultados(
        caminho,
        [
            _resultado("11.222.333/0001-81", "NEGATIVA", "ceuazul-pr"),
            _resultado("40.734.037/0001-68", "POSITIVA", "toledo-pr"),
        ],
    )

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    assert dados["11222333000181"] == {"municipal": "NEGATIVA"}
    assert dados["40734037000168"] == {"municipal": "POSITIVA"}


def test_registrar_resultados_ignora_portal_sem_coluna_no_painel(tmp_path):
    caminho = tmp_path / "resultados.json"

    registrar_resultados(caminho, [_resultado("11.222.333/0001-81", "NEGATIVA", "portal-novo")])

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    assert dados == {}
