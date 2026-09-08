"""CLI da consulta semi-automática via navegador (RFB e CNDT)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .navegador import PORTAIS, consultar_lista
from .planilha import ler_cnpjs_csv
from .resumo import houve_situacao_desconhecida, linha_resumo


def main() -> None:
    lista_portais = "; ".join(f"{chave}={info['nome']}" for chave, info in PORTAIS.items())

    parser = argparse.ArgumentParser(
        prog="consulta-cnd-navegador",
        description=(
            "Consulta semi-automática de certidões negativas pelo navegador: "
            "abre a página de consulta do portal escolhido; você faz login "
            "se for pedido, digita o CNPJ e resolve o CAPTCHA manualmente "
            "para cada cliente."
        ),
    )
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--cnpj", action="append", help="CNPJ a consultar (pode repetir).")
    grupo.add_argument("--arquivo", help="CSV com uma coluna 'cnpj' listando os clientes.")
    parser.add_argument("--coluna", default="cnpj", help="Nome da coluna de CNPJ no CSV.")
    parser.add_argument(
        "--portal",
        choices=sorted(PORTAIS),
        default="rfb",
        help=f"Qual certidão consultar: {lista_portais} (padrão: rfb).",
    )
    parser.add_argument(
        "--pasta-destino",
        default="certidoes",
        help="Pasta onde salvar os PDFs baixados (padrão: ./certidoes).",
    )
    parser.add_argument(
        "--pasta-perfil",
        help=(
            "Pasta de perfil do navegador, para manter login entre "
            "execuções (padrão: ~/.consulta_cnd/perfil_navegador)."
        ),
    )
    args = parser.parse_args()

    cnpjs = args.cnpj if args.cnpj else ler_cnpjs_csv(args.arquivo, args.coluna)
    argumentos_extra = {"pasta_perfil": Path(args.pasta_perfil)} if args.pasta_perfil else {}
    resultados = consultar_lista(
        cnpjs, Path(args.pasta_destino), portal=args.portal, **argumentos_extra
    )

    print("\nResumo:")
    for resultado in resultados:
        print(linha_resumo(resultado))

    if houve_situacao_desconhecida(resultados):
        sys.exit(1)


if __name__ == "__main__":
    main()
