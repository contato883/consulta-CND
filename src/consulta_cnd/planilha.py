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
