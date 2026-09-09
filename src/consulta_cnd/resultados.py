"""
Persistência dos resultados de consulta em `resultados.json`, no formato
que `consulta-cnd-painel` espera: {cnpj_limpo: {tipo_certidao: situacao}}.

Isso fecha o ciclo entre as ferramentas de consulta (`consulta-cnd-navegador`,
`consulta-cnd-rotina`) e o painel local: cada consulta feita atualiza o
arquivo automaticamente, sem precisar montar o JSON à mão.
"""

from __future__ import annotations

import json
from pathlib import Path

from .cnpj import limpar_cnpj
from .models import ResultadoCertidao

# Cada portal do navegador.PORTAIS alimenta uma coluna do painel; os cinco
# portais municipais (um por cidade) convergem todos na mesma coluna
# "municipal" — o painel não distingue qual prefeitura, só o tipo.
PORTAL_PARA_TIPO = {
    "rfb": "rfb",
    "pr": "pr",
    "cndt": "cndt",
    "fgts": "fgts",
    "ceuazul-pr": "municipal",
    "cascavel-pr": "municipal",
    "toledo-pr": "municipal",
    "veracruzdooeste-pr": "municipal",
    "medianeira-pr": "municipal",
}


def _carregar(caminho: Path) -> dict[str, dict[str, str]]:
    if not caminho.exists():
        return {}
    return json.loads(caminho.read_text(encoding="utf-8"))


def registrar_resultados(
    caminho_resultados: str | Path, resultados: list[ResultadoCertidao]
) -> None:
    """
    Mescla `resultados` no `resultados.json` existente (uma leitura, uma
    escrita) e salva. Um resultado cujo portal não tem coluna no painel é
    ignorado silenciosamente — nunca interrompe a consulta por causa disso.
    """
    caminho = Path(caminho_resultados)
    dados = _carregar(caminho)

    for resultado in resultados:
        portal = resultado.resposta_bruta.get("portal")
        tipo = PORTAL_PARA_TIPO.get(portal)
        if tipo is None:
            continue
        numero = limpar_cnpj(resultado.cnpj)
        dados.setdefault(numero, {})[tipo] = resultado.situacao

    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
