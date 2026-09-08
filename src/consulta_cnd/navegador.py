"""
Consulta semi-automática de CND no portal público da Receita Federal/PGFN,
usando um navegador real (Playwright) — sem tentar contornar o CAPTCHA.

Fluxo por CNPJ:
  1. O script abre o portal e preenche o CNPJ automaticamente.
  2. Você resolve o CAPTCHA e clica no botão de consulta/emissão manualmente.
  3. Você pressiona Enter no terminal e o script segue para o próximo CNPJ,
     salvando o PDF baixado e tentando identificar a situação no texto da página.

[A VERIFICAR] Não foi possível acessar solucoes.receita.fazenda.gov.br a
partir do ambiente onde este código foi escrito (bloqueio de rede), então os
seletores abaixo não puderam ser confirmados contra a página real. Antes do
primeiro uso: abra a página no navegador, clique com o botão direito no campo
de CNPJ → Inspecionar, e ajuste `SELETOR_CAMPO_CNPJ` (e os textos dos botões,
se usados) conforme o que você encontrar. É um ajuste único de ~2 minutos.
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

URL_EMISSAO_PJ = "https://solucoes.receita.fazenda.gov.br/servicos/certidaointernet/pj/emitir"

# [A VERIFICAR] confirmar na página real antes do primeiro uso.
SELETOR_CAMPO_CNPJ = "#NI"
TEXTO_BOTAO_CONSULTAR = "Consultar"
TEXTO_BOTAO_EMITIR = "Emitir Certidão"

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


def consultar_cnpj_no_portal(page: Page, cnpj: str, pasta_destino: Path) -> ResultadoCertidao:
    numero = limpar_cnpj(cnpj)
    pasta_destino.mkdir(parents=True, exist_ok=True)

    pdfs_baixados: list[Path] = []

    def _ao_baixar(download):
        caminho = pasta_destino / f"{numero}.pdf"
        download.save_as(caminho)
        pdfs_baixados.append(caminho)

    page.on("download", _ao_baixar)
    try:
        page.goto(URL_EMISSAO_PJ)
        page.fill(SELETOR_CAMPO_CNPJ, numero)

        input(
            f"\n>>> CNPJ {formatar_cnpj(numero)} preenchido no navegador.\n"
            f">>> Resolva o CAPTCHA e clique em '{TEXTO_BOTAO_CONSULTAR}' / "
            f"'{TEXTO_BOTAO_EMITIR}'.\n"
            f">>> Quando a certidão aparecer na tela, pressione Enter aqui "
            f"para continuar... "
        )

        texto_pagina = page.content()
    finally:
        page.remove_listener("download", _ao_baixar)

    situacao = detectar_situacao(texto_pagina)
    caminho_pdf = pdfs_baixados[0] if pdfs_baixados else None

    return ResultadoCertidao(
        cnpj=numero,
        situacao=situacao or "DESCONHECIDA",
        resposta_bruta={"pdf": str(caminho_pdf) if caminho_pdf else None},
    )


def consultar_lista(cnpjs: list[str], pasta_destino: Path) -> list[ResultadoCertidao]:
    from playwright.sync_api import sync_playwright

    resultados = []
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(headless=False)
        pagina = navegador.new_page()
        try:
            for cnpj in cnpjs:
                resultados.append(consultar_cnpj_no_portal(pagina, cnpj, pasta_destino))
        finally:
            navegador.close()
    return resultados
