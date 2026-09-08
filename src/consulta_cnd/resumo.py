"""Formatação do resumo textual de resultados de consulta."""

from __future__ import annotations

from .cnpj import formatar_cnpj
from .models import ResultadoCertidao


def linha_resumo(resultado: ResultadoCertidao) -> str:
    if resultado.situacao == "DESCONHECIDA":
        status = "CONFERIR PDF"
    elif resultado.regular:
        status = "OK"
    else:
        status = "PENDÊNCIA"
    return f"{formatar_cnpj(resultado.cnpj)}  {resultado.situacao:<30} [{status}]"


def houve_situacao_desconhecida(resultados: list[ResultadoCertidao]) -> bool:
    return any(resultado.situacao == "DESCONHECIDA" for resultado in resultados)
