"""CLI da rotina mensal: RFB + CNDT + Estadual-PR + municipal por cliente."""

from __future__ import annotations

import argparse
from pathlib import Path

from .rotina import executar_rotina


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="consulta-cnd-rotina",
        description=(
            "Roda a rotina mensal de CND para todos os CNPJs de uma planilha: "
            "RFB, CNDT e Estadual-PR para todos, mais a CND municipal de cada "
            "cliente conforme o município (quando o portal já estiver "
            "cadastrado). Não inclui o CRF/FGTS — rode-o à parte com "
            "consulta-cnd-navegador --portal fgts para os clientes com "
            "empregados."
        ),
    )
    parser.add_argument(
        "--arquivo",
        default="clientes.csv",
        help="CSV com colunas 'cnpj' e 'municipio' (padrão: clientes.csv).",
    )
    parser.add_argument(
        "--pasta-destino",
        default="certidoes",
        help="Pasta onde salvar os PDFs baixados (padrão: ./certidoes).",
    )
    args = parser.parse_args()

    executar_rotina(args.arquivo, Path(args.pasta_destino))


if __name__ == "__main__":
    main()
