import pytest

from consulta_cnd.planilha import ler_clientes_csv, ler_cnpjs_csv


def test_ler_cnpjs_csv(tmp_path):
    caminho = tmp_path / "clientes.csv"
    caminho.write_text("cnpj,razao_social\n11.222.333/0001-81,Empresa Fictícia LTDA\n")

    cnpjs = ler_cnpjs_csv(caminho)

    assert cnpjs == ["11.222.333/0001-81"]


def test_ler_cnpjs_csv_coluna_customizada(tmp_path):
    caminho = tmp_path / "clientes.csv"
    caminho.write_text("documento\n11.222.333/0001-81\n")

    cnpjs = ler_cnpjs_csv(caminho, coluna="documento")

    assert cnpjs == ["11.222.333/0001-81"]


def test_ler_cnpjs_csv_coluna_ausente_levanta_erro(tmp_path):
    caminho = tmp_path / "clientes.csv"
    caminho.write_text("razao_social\nEmpresa Fictícia LTDA\n")

    with pytest.raises(ValueError):
        ler_cnpjs_csv(caminho)


def test_ler_clientes_csv(tmp_path):
    caminho = tmp_path / "clientes.csv"
    caminho.write_text(
        "cnpj,razao_social,municipio,uf\n"
        "11.222.333/0001-81,Empresa Fictícia LTDA,CEU AZUL,PR\n"
    )

    clientes = ler_clientes_csv(caminho)

    assert clientes == [
        {
            "cnpj": "11.222.333/0001-81",
            "municipio": "CEU AZUL",
            "razao_social": "Empresa Fictícia LTDA",
        }
    ]


def test_ler_clientes_csv_sem_colunas_opcionais_usa_vazio(tmp_path):
    caminho = tmp_path / "clientes.csv"
    caminho.write_text("cnpj\n11.222.333/0001-81\n")

    clientes = ler_clientes_csv(caminho)

    assert clientes == [{"cnpj": "11.222.333/0001-81", "municipio": "", "razao_social": ""}]


def test_ler_clientes_csv_coluna_cnpj_ausente_levanta_erro(tmp_path):
    caminho = tmp_path / "clientes.csv"
    caminho.write_text("razao_social\nEmpresa Fictícia LTDA\n")

    with pytest.raises(ValueError):
        ler_clientes_csv(caminho)
