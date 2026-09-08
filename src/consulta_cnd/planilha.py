"""Leitura de lista de CNPJs a partir de uma planilha CSV."""

from __future__ import annotations

import csv
from pathlib import Path


def ler_cnpjs_csv(caminho: str | Path, coluna: str = "cnpj") -> list[str]:
    caminho = Path(caminho)
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = leitor.fieldnames or []
        if coluna not in colunas:
            raise ValueError(
                f"Coluna '{coluna}' não encontrada em {caminho}. Colunas disponíveis: {colunas}"
            )
        return [linha[coluna].strip() for linha in leitor if linha[coluna].strip()]


def ler_clientes_csv(
    caminho: str | Path,
    coluna_cnpj: str = "cnpj",
    coluna_municipio: str = "municipio",
) -> list[dict[str, str]]:
    """Lê CNPJ + município de cada cliente (município ausente vira string vazia)."""
    caminho = Path(caminho)
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = leitor.fieldnames or []
        if coluna_cnpj not in colunas:
            raise ValueError(
                f"Coluna '{coluna_cnpj}' não encontrada em {caminho}. Colunas disponíveis: {colunas}"
            )
        clientes = []
        for linha in leitor:
            cnpj = linha[coluna_cnpj].strip()
            if not cnpj:
                continue
            clientes.append(
                {"cnpj": cnpj, "municipio": linha.get(coluna_municipio, "").strip()}
            )
        return clientes
