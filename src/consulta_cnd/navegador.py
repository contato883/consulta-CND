"""
Consulta semi-automática de certidões negativas usando um navegador real
(Playwright) — sem tentar contornar login gov.br nem CAPTCHA.

Portais suportados (ver PORTAIS):
  - "rfb": CND Federal (Receita Federal/PGFN), no novo Portal de Serviços
    Digitais — exige login com conta gov.br (nível Prata ou Ouro).
  - "cndt": CNDT — Certidão Negativa de Débitos Trabalhistas (TST) —
    normalmente sem login, só CNPJ + CAPTCHA.

Fluxo por CNPJ, em qualquer portal:
  1. O script abre a página de consulta do portal escolhido.
  2. Você faz login (se for pedido), digita o CNPJ, resolve o CAPTCHA, e
     consulta/emite a certidão.
  3. Você pressiona Enter no terminal e o script segue para o próximo CNPJ,
     salvando o PDF baixado (se houver) e tentando identificar a situação no
     texto da página resultante.

O navegador roda com um perfil persistente (por padrão em
`~/.consulta_cnd/perfil_navegador`, fora do repositório), então logins
feitos numa execução tendem a continuar valendo nas seguintes.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from .cnpj import formatar_cnpj, limpar_cnpj
from .models import ResultadoCertidao

if TYPE_CHECKING:
    # Import isolado do playwright (dependência opcional, extra "navegador")
    # para não exigir instalação só para rodar os testes de `detectar_situacao`.
    from playwright.sync_api import Page

PASTA_PERFIL_PADRAO = Path.home() / ".consulta_cnd" / "perfil_navegador"

PORTAIS: dict[str, dict[str, str]] = {
    "rfb": {
        "url": "https://servicos.receitafederal.gov.br/servico/certidoes/#/home/cnpj",
        "nome": "CND Federal (Receita Federal/PGFN)",
    },
    "cndt": {
        "url": "https://cndt-certidao.tst.jus.br/",
        "nome": "CNDT — Débitos Trabalhistas (TST)",
    },
}

_PADRAO_SITUACAO = re.compile(
    r"CERTID[ÃA]O\s+(NEGATIVA|POSITIVA\s+COM\s+EFEITO\s+DE\s+NEGATIVA|POSITIVA)",
    re.IGNORECASE,
)


def detectar_situacao(texto_pagina: str) -> str | None:
    """
    Extrai a situação (NEGATIVA / POSITIVA_COM_EFEITO_DE_NEGATIVA / POSITIVA)
    do texto da página de resultado. Retorna None se não identificar — nesse
    caso, confira o PDF baixado manualmente.
    """
    encontrado = _PADRAO_SITUACAO.search(texto_pagina)
    if not encontrado:
        return None
    return re.sub(r"\s+", "_", encontrado.group(1).upper())


def _validar_portal(portal: str) -> None:
    if portal not in PORTAIS:
        raise ValueError(f"Portal desconhecido: {portal!r}. Opções: {sorted(PORTAIS)}")


def consultar_cnpj_no_portal(
    page: Page, cnpj: str, pasta_destino: Path, portal: str = "rfb"
) -> ResultadoCertidao:
    _validar_portal(portal)
    numero = limpar_cnpj(cnpj)
    pasta_destino.mkdir(parents=True, exist_ok=True)

    pdfs_baixados: list[Path] = []

    def _ao_baixar(download):
        caminho = pasta_destino / f"{numero}_{portal}.pdf"
        download.save_as(caminho)
        pdfs_baixados.append(caminho)

    page.on("download", _ao_baixar)
    try:
        page.goto(PORTAIS[portal]["url"])

        input(
            f"\n>>> {PORTAIS[portal]['nome']} — CNPJ {formatar_cnpj(numero)}.\n"
            f">>> Na janela do navegador: faça login se for pedido, digite "
            f"o CNPJ, resolva o CAPTCHA, e consulte/emita a certidão.\n"
            f">>> Quando o resultado aparecer na tela, pressione Enter "
            f"aqui para continuar... "
        )

        texto_pagina = page.content()
    finally:
        page.remove_listener("download", _ao_baixar)

    situacao = detectar_situacao(texto_pagina)
    caminho_pdf = pdfs_baixados[0] if pdfs_baixados else None

    return ResultadoCertidao(
        cnpj=numero,
        situacao=situacao or "DESCONHECIDA",
        resposta_bruta={"portal": portal, "pdf": str(caminho_pdf) if caminho_pdf else None},
    )


def consultar_lista(
    cnpjs: list[str],
    pasta_destino: Path,
    portal: str = "rfb",
    pasta_perfil: Path = PASTA_PERFIL_PADRAO,
) -> list[ResultadoCertidao]:
    _validar_portal(portal)

    from playwright.sync_api import sync_playwright

    pasta_perfil.mkdir(parents=True, exist_ok=True)

    resultados = []
    with sync_playwright() as playwright:
        contexto = playwright.chromium.launch_persistent_context(
            str(pasta_perfil), headless=False
        )
        pagina = contexto.pages[0] if contexto.pages else contexto.new_page()
        try:
            for cnpj in cnpjs:
                resultados.append(consultar_cnpj_no_portal(pagina, cnpj, pasta_destino, portal))
        finally:
            contexto.close()
    return resultados
