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
            "Consulta semi-automática de CND no Portal de Serviços Digitais "
            "da Receita Federal: abre o navegador na página de consulta; "
            "você faz login no gov.br, digita o CNPJ e resolve o CAPTCHA "
            "manualmente para cada cliente."
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
    parser.add_argument(
        "--pasta-perfil",
        help=(
            "Pasta de perfil do navegador, para manter o login do gov.br "
            "entre execuções (padrão: ~/.consulta_cnd/perfil_navegador)."
        ),
    )
    args = parser.parse_args()

    cnpjs = args.cnpj if args.cnpj else ler_cnpjs_csv(args.arquivo, args.coluna)
    argumentos_extra = {"pasta_perfil": Path(args.pasta_perfil)} if args.pasta_perfil else {}
    resultados = consultar_lista(cnpjs, Path(args.pasta_destino), **argumentos_extra)

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
