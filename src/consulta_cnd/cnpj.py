"""Validação e formatação de CNPJ."""

from __future__ import annotations


def limpar_cnpj(cnpj: str) -> str:
    """Remove tudo que não for dígito."""
    return "".join(caractere for caractere in cnpj if caractere.isdigit())


def _calcular_dv(base: str, pesos: list[int]) -> int:
    soma = sum(int(digito) * peso for digito, peso in zip(base, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def cnpj_valido(cnpj: str) -> bool:
    """Valida os dígitos verificadores de um CNPJ (aceita com ou sem máscara)."""
    numeros = limpar_cnpj(cnpj)
    if len(numeros) != 14 or len(set(numeros)) == 1:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    dv1 = _calcular_dv(numeros[:12], pesos1)
    dv2 = _calcular_dv(numeros[:12] + str(dv1), pesos2)

    return numeros[-2:] == f"{dv1}{dv2}"


def formatar_cnpj(cnpj: str) -> str:
    """Formata um CNPJ (com ou sem máscara) como XX.XXX.XXX/XXXX-XX."""
    numeros = limpar_cnpj(cnpj)
    if len(numeros) != 14:
        return cnpj
    return f"{numeros[0:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:14]}"
