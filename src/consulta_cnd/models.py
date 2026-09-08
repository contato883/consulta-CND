"""Modelos de dados do resultado de uma consulta de CND."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SITUACOES_REGULARES = {"NEGATIVA", "POSITIVA_COM_EFEITO_DE_NEGATIVA", "REGULAR"}


@dataclass
class ResultadoCertidao:
    cnpj: str
    situacao: str
    numero_certidao: str | None = None
    data_emissao: str | None = None
    data_validade: str | None = None
    resposta_bruta: dict[str, Any] = field(default_factory=dict)

    @property
    def regular(self) -> bool:
        """True se a situação for NEGATIVA, POSITIVA COM EFEITO DE NEGATIVA ou REGULAR."""
        return self.situacao in SITUACOES_REGULARES
