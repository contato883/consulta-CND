"""
Gera um painel HTML local com a situação das certidões por empresa.

Este painel é só uma VISUALIZAÇÃO — ele não consulta nada sozinho. As
situações vêm de um arquivo `resultados.json` (formato: {cnpj_limpo: {tipo:
situacao}}, com o CNPJ só em dígitos), produzido depois de rodar
`consulta-cnd-rotina` / `consulta-cnd-navegador` de verdade. Sem esse
arquivo (ou para uma empresa sem entrada nele), a célula aparece como
"PENDENTE DE VERIFICAÇÃO" — nunca como "REGULAR" por omissão, para não
sugerir uma regularidade que não foi checada.
"""

from __future__ import annotations

import base64
import html
import json
from datetime import datetime
from pathlib import Path

from .cnpj import formatar_cnpj, limpar_cnpj
from .models import SITUACOES_REGULARES
from .planilha import ler_clientes_csv
from .rotina import MAPA_MUNICIPIO_PORTAL

TIPOS_CERTIDAO = [
    ("rfb", "Federal (RFB/PGFN)"),
    ("pr", "Estadual (PR)"),
    ("municipal", "Municipal"),
    ("cndt", "Trabalhista (CNDT)"),
    ("fgts", "CRF/FGTS"),
]


def _status_celula(situacao: str | None) -> tuple[str, str]:
    """(texto, classe_css) para uma situação — None = ainda não consultado."""
    if situacao is None:
        return "PENDENTE DE VERIFICAÇÃO", "pendente"
    if situacao in SITUACOES_REGULARES:
        return "REGULAR", "regular"
    return f"PENDÊNCIA ({situacao})", "irregular"


def _portal_municipal(municipio: str) -> str | None:
    return MAPA_MUNICIPIO_PORTAL.get(municipio.strip().upper())


def _logo_base64(caminho_logo: str | Path | None) -> str | None:
    if not caminho_logo:
        return None
    caminho_logo = Path(caminho_logo)
    if not caminho_logo.exists():
        return None
    return base64.b64encode(caminho_logo.read_bytes()).decode("ascii")


def _linha_html(cliente: dict[str, str], resultados_do_cliente: dict[str, str]) -> str:
    numero = cliente["cnpj"]
    municipio = cliente["municipio"]
    celulas = []
    for chave, _rotulo in TIPOS_CERTIDAO:
        if chave == "municipal" and not _portal_municipal(municipio):
            texto, classe = "SEM PORTAL CADASTRADO", "sem-portal"
        else:
            texto, classe = _status_celula(resultados_do_cliente.get(chave))
        celulas.append(f'<td><span class="badge {classe}">{html.escape(texto)}</span></td>')

    return (
        "<tr>"
        f"<td class=\"empresa\">{html.escape(cliente['razao_social'] or numero)}</td>"
        f"<td>{html.escape(formatar_cnpj(numero))}</td>"
        f"<td>{html.escape(municipio)}</td>"
        + "".join(celulas)
        + "</tr>"
    )


def gerar_painel_html(
    caminho_clientes: str | Path,
    caminho_logo: str | Path | None = None,
    caminho_resultados: str | Path | None = None,
) -> str:
    clientes = ler_clientes_csv(caminho_clientes)
    clientes.sort(key=lambda cliente: (cliente["razao_social"] or cliente["cnpj"]).upper())

    resultados: dict[str, dict[str, str]] = {}
    if caminho_resultados and Path(caminho_resultados).exists():
        resultados = json.loads(Path(caminho_resultados).read_text(encoding="utf-8"))

    logo_b64 = _logo_base64(caminho_logo)
    logo_html = (
        f'<img src="data:image/jpeg;base64,{logo_b64}" alt="Logo" class="logo">' if logo_b64 else ""
    )

    cabecalho_colunas = "".join(f"<th>{html.escape(rotulo)}</th>" for _chave, rotulo in TIPOS_CERTIDAO)
    linhas = "".join(
        _linha_html(cliente, resultados.get(limpar_cnpj(cliente["cnpj"]), {}))
        for cliente in clientes
    )
    gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M")
    fonte_dados = (
        "dados de exemplo — nenhuma consulta real foi realizada ainda"
        if not resultados
        else f"última atualização com resultados reais: {gerado_em}"
    )

    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Painel de Certidões — PERINAZZO CONTABILIDADE</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; background: #f4f5f7; color: #1f2937; margin: 0; padding: 32px; }}
  header {{ display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }}
  .logo {{ height: 56px; width: auto; border-radius: 4px; }}
  h1 {{ font-size: 20px; margin: 0; }}
  .subtitulo {{ color: #6b7280; font-size: 13px; margin-top: 2px; }}
  .aviso {{ background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; padding: 10px 14px; border-radius: 6px; font-size: 13px; margin-bottom: 20px; }}
  table {{ border-collapse: collapse; width: 100%; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  th, td {{ padding: 10px 12px; text-align: left; font-size: 13px; border-bottom: 1px solid #e5e7eb; }}
  th {{ background: #111827; color: #fff; font-weight: 600; white-space: nowrap; }}
  td.empresa {{ font-weight: 600; }}
  tr:last-child td {{ border-bottom: none; }}
  .badge {{ display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; white-space: nowrap; }}
  .badge.regular {{ background: #d1fae5; color: #065f46; }}
  .badge.irregular {{ background: #fee2e2; color: #991b1b; }}
  .badge.pendente {{ background: #fef3c7; color: #92400e; }}
  .badge.sem-portal {{ background: #e5e7eb; color: #4b5563; }}
  footer {{ margin-top: 20px; font-size: 12px; color: #6b7280; }}
</style>
</head>
<body>
<header>
  {logo_html}
  <div>
    <h1>Painel de Certidões — Situação por Empresa</h1>
    <div class="subtitulo">PERINAZZO CONTABILIDADE — uso interno, gerado em {gerado_em}</div>
  </div>
</header>
<div class="aviso">⚠ {html.escape(fonte_dados)}. "PENDENTE DE VERIFICAÇÃO" significa que a certidão ainda não foi consultada — não é uma confirmação de regularidade.</div>
<table>
<thead><tr><th>Empresa</th><th>CNPJ</th><th>Município</th>{cabecalho_colunas}</tr></thead>
<tbody>
{linhas}
</tbody>
</table>
<footer>Documento confidencial — uso interno da PERINAZZO CONTABILIDADE. Não distribuir.</footer>
</body>
</html>
"""
