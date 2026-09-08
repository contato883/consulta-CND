"""
Consulta semi-automática de certidões negativas usando um navegador real
(Playwright) — sem tentar contornar login gov.br nem CAPTCHA.

Portais suportados (ver PORTAIS):
  - "rfb": CND Federal (Receita Federal/PGFN), no novo Portal de Serviços
    Digitais — exige login com conta gov.br (nível Prata ou Ouro).
  - "cndt": CNDT — Certidão Negativa de Débitos Trabalhistas (TST) —
    normalmente sem login, só CNPJ + CAPTCHA.
  - "pr": CND Estadual do Paraná (Sefa/PR) — exige login com Nota Paraná ou
    conta Receita/PR.
  - "ceuazul-pr": CND Municipal de Céu Azul/PR (plataforma atende.net) —
    normalmente sem login, só CNPJ + CAPTCHA.
  - "cascavel-pr": CND Municipal de Cascavel/PR (mesma plataforma, em
    domínio próprio da prefeitura) — normalmente sem login, só CNPJ +
    CAPTCHA.
  - "fgts": CRF — Certificado de Regularidade do FGTS (Caixa) —
    normalmente sem login, só CNPJ + CAPTCHA. Só se aplica a empresas com
    empregados/FGTS recolhido — não confundir com CND, CNDT etc.
  - "toledo-pr": CND Municipal de Toledo/PR (plataforma Equiplano) —
    [A VERIFICAR] pode exigir login/cadastro além de CNPJ + CAPTCHA; não
    foi possível confirmar contra a página real (acesso bloqueado no
    ambiente onde este código foi escrito).
  - "veracruzdooeste-pr": CND Municipal de Vera Cruz do Oeste/PR
    (plataforma Betha Cidadão Web) — normalmente sem login, só CNPJ +
    CAPTCHA.
  - "medianeira-pr": CND Municipal de Medianeira/PR (plataforma Elotech) —
    [A VERIFICAR] não foi possível confirmar se exige login além de CNPJ +
    CAPTCHA (acesso bloqueado no ambiente onde este código foi escrito).

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
    "pr": {
        "url": "https://cdwfazenda.paas.pr.gov.br/cdwportal/certidao/automatica",
        "nome": "CND Estadual — Paraná (Sefa/PR)",
    },
    "ceuazul-pr": {
        "url": "https://ceuazul.atende.net/autoatendimento/servicos/certidao-negativa-de-debitos/detalhar/1",
        "nome": "CND Municipal — Céu Azul/PR",
    },
    "cascavel-pr": {
        "url": "https://prefa.cascavel.pr.gov.br/autoatendimento/servicos/certidao-negativa-de-debitos/detalhar/1",
        "nome": "CND Municipal — Cascavel/PR",
    },
    "fgts": {
        "url": "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf",
        "nome": "CRF — Regularidade do FGTS (Caixa)",
    },
    "toledo-pr": {
        "url": "http://equiplano.toledo.pr.gov.br:7474/esportal/stmcertidao.load.logic",
        "nome": "CND Municipal — Toledo/PR",
    },
    "veracruzdooeste-pr": {
        "url": "https://e-gov.betha.com.br/cdweb/03114-574/contribuinte/rel_cndcontribuinte.faces",
        "nome": "CND Municipal — Vera Cruz do Oeste/PR",
    },
    "medianeira-pr": {
        "url": "https://medianeira.oxy.elotech.com.br/portal-contribuinte/emissao-certidoes",
        "nome": "CND Municipal — Medianeira/PR",
    },
}

_PADRAO_SITUACAO_CND = re.compile(
    r"CERTID[ÃA]O\s+(NEGATIVA|POSITIVA\s+COM\s+EFEITO\s+DE\s+NEGATIVA|POSITIVA)",
    re.IGNORECASE,
)
# [A VERIFICAR] O texto real da página de resultado do CRF/FGTS não pôde ser
# confirmado (acesso a consulta-crf.caixa.gov.br bloqueado no ambiente onde
# este código foi escrito). REGULAR/IRREGULAR é a terminologia oficial do
# certificado, mas o padrão exato da página pode divergir — confira o PDF.
_PADRAO_SITUACAO_FGTS = re.compile(r"\b(IRREGULAR|REGULAR)\b", re.IGNORECASE)


def detectar_situacao(texto_pagina: str) -> str | None:
    """
    Extrai a situação do texto da página de resultado:
      - Certidões de débito (CND, CNDT, estadual, municipal): NEGATIVA /
        POSITIVA_COM_EFEITO_DE_NEGATIVA / POSITIVA.
      - CRF/FGTS: REGULAR / IRREGULAR.
    Retorna None se não identificar — nesse caso, confira o PDF baixado
    manualmente.
    """
    encontrado_cnd = _PADRAO_SITUACAO_CND.search(texto_pagina)
    if encontrado_cnd:
        return re.sub(r"\s+", "_", encontrado_cnd.group(1).upper())

    encontrado_fgts = _PADRAO_SITUACAO_FGTS.search(texto_pagina)
    if encontrado_fgts:
        return encontrado_fgts.group(1).upper()

    return None


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
