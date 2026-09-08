"""CLI para consultar a CND de um ou mais CNPJs."""

from __future__ import annotations

import argparse
import os
import sys

from .auth import SerproAuth, SerproAuthError
from .client import ConsultaCndClient, ConsultaCndError
from .cnpj import formatar_cnpj
from .planilha import ler_cnpjs_csv


def _construir_client() -> ConsultaCndClient:
    consumer_key = os.environ.get("SERPRO_CONSUMER_KEY")
    consumer_secret = os.environ.get("SERPRO_CONSUMER_SECRET")
    if not consumer_key or not consumer_secret:
        sys.exit("Defina SERPRO_CONSUMER_KEY e SERPRO_CONSUMER_SECRET (veja .env.example).")

    producao = os.environ.get("SERPRO_AMBIENTE", "trial").lower() == "producao"
    auth = SerproAuth(consumer_key, consumer_secret)
    return ConsultaCndClient(auth, producao=producao)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="consulta-cnd",
        description="Consulta automatizada de CND (RFB/PGFN) para CNPJs de clientes.",
    )
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--cnpj", action="append", help="CNPJ a consultar (pode repetir).")
    grupo.add_argument("--arquivo", help="CSV com uma coluna 'cnpj' listando os clientes.")
    parser.add_argument(
        "--coluna", default="cnpj", help="Nome da coluna de CNPJ no CSV (padrão: cnpj)."
    )
    args = parser.parse_args()

    cnpjs = args.cnpj if args.cnpj else ler_cnpjs_csv(args.arquivo, args.coluna)
    client = _construir_client()

    codigo_saida = 0
    for cnpj in cnpjs:
        try:
            resultado = client.consultar(cnpj)
            status = "OK" if resultado.regular else "PENDÊNCIA"
            print(f"{formatar_cnpj(cnpj)}  {resultado.situacao:<30} [{status}]")
        except (ConsultaCndError, SerproAuthError) as erro:
            codigo_saida = 1
            print(f"{formatar_cnpj(cnpj)}  ERRO: {erro}")

    sys.exit(codigo_saida)


if __name__ == "__main__":
    main()
