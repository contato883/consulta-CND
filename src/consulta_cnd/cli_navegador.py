"""CLI da consulta semi-automática via navegador (portal público RFB/PGFN)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .cnpj import formatar_cnpj
from .navegador import consultar_lista
from .planilha import ler_cnpjs_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="consulta-cnd-navegador",
        description=(
            "Consulta semi-automática de CND no portal público da Receita "
            "Federal/PGFN: abre um navegador e preenche o CNPJ de cada "
            "cliente automaticamente; você resolve o CAPTCHA manualmente "
            "para cada um."
        ),
    )
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--cnpj", action="append", help="CNPJ a consultar (pode repetir).")
    grupo.add_argument("--arquivo", help="CSV com uma coluna 'cnpj' listando os clientes.")
    parser.add_argument("--coluna", default="cnpj", help="Nome da coluna de CNPJ no CSV.")
    parser.add_argument(
        "--pasta-destino",
        default="certidoes",
        help="Pasta onde salvar os PDFs baixados (padrão: ./certidoes).",
    )
    args = parser.parse_args()

    cnpjs = args.cnpj if args.cnpj else ler_cnpjs_csv(args.arquivo, args.coluna)
    resultados = consultar_lista(cnpjs, Path(args.pasta_destino))

    print("\nResumo:")
    for resultado in resultados:
        if resultado.situacao == "DESCONHECIDA":
            status = "CONFERIR PDF"
        elif resultado.regular:
            status = "OK"
        else:
            status = "PENDÊNCIA"
        print(f"{formatar_cnpj(resultado.cnpj)}  {resultado.situacao:<30} [{status}]")

    if any(resultado.situacao == "DESCONHECIDA" for resultado in resultados):
        sys.exit(1)


if __name__ == "__main__":
    main()
