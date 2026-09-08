"""CLI para gerar o painel HTML local de situação das certidões."""

from __future__ import annotations

import argparse
from pathlib import Path

from .painel import gerar_painel_html


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="consulta-cnd-painel",
        description=(
            "Gera uma página HTML local com a situação das certidões por "
            "empresa (Federal, Estadual, Municipal, Trabalhista, CRF/FGTS). "
            "Sem --resultados, tudo aparece como 'PENDENTE DE VERIFICAÇÃO' — "
            "esta ferramenta não consulta nada sozinha."
        ),
    )
    parser.add_argument(
        "--arquivo", default="clientes.csv", help="CSV de clientes (padrão: clientes.csv)."
    )
    parser.add_argument("--logo", help="Caminho de uma imagem (jpg/png) para o cabeçalho.")
    parser.add_argument(
        "--resultados",
        help="JSON com resultados reais: {cnpj: {rfb|pr|municipal|cndt|fgts: situacao}}.",
    )
    parser.add_argument(
        "--saida",
        default="painel_certidoes.html",
        help="Arquivo HTML de saída (padrão: painel_certidoes.html).",
    )
    args = parser.parse_args()

    html_gerado = gerar_painel_html(args.arquivo, args.logo, args.resultados)
    Path(args.saida).write_text(html_gerado, encoding="utf-8")
    print(f"Painel gerado em {args.saida}")


if __name__ == "__main__":
    main()
