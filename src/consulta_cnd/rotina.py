"""
Rotina mensal de consulta de certidões para a carteira de clientes, por CNPJ.

Roda, na sequência: os portais que valem para toda a carteira PR (RFB, CNDT,
Estadual-PR) e, depois, o portal municipal de cada cliente conforme o
município na planilha — quando esse município já tem um portal cadastrado
em MAPA_MUNICIPIO_PORTAL. Município sem portal configurado é listado à
parte, sem consulta — não há como adivinhar a URL certa daquela prefeitura.

Não inclui o portal "fgts" (CRF) — esse só se aplica a clientes com
empregados, então fica de fora da rotina padrão; rode-o à parte quando
fizer sentido:
    consulta-cnd-navegador --arquivo clientes.csv --portal fgts
"""

from __future__ import annotations

from pathlib import Path

from .navegador import PORTAIS, consultar_lista
from .planilha import ler_clientes_csv
from .resumo import linha_resumo

PORTAIS_PARA_TODA_CARTEIRA = ["rfb", "cndt", "pr"]

MAPA_MUNICIPIO_PORTAL = {
    "CEU AZUL": "ceuazul-pr",
    "CASCAVEL": "cascavel-pr",
    "TOLEDO": "toledo-pr",
    "VERA CRUZ DO OESTE": "veracruzdooeste-pr",
    "MEDIANEIRA": "medianeira-pr",
}


def montar_plano(
    clientes: list[dict[str, str]],
) -> tuple[list[tuple[str, list[str]]], list[str]]:
    """
    Monta o plano de execução: lista de (portal, cnpjs) na ordem em que
    devem rodar, e a lista de municípios da carteira sem portal municipal
    configurado ainda.
    """
    todos_os_cnpjs = [cliente["cnpj"] for cliente in clientes]
    plano = [(portal, todos_os_cnpjs) for portal in PORTAIS_PARA_TODA_CARTEIRA]

    municipios_presentes = {
        cliente["municipio"].strip().upper() for cliente in clientes if cliente.get("municipio")
    }
    municipios_sem_portal = sorted(municipios_presentes - MAPA_MUNICIPIO_PORTAL.keys())

    for municipio, portal in MAPA_MUNICIPIO_PORTAL.items():
        cnpjs_do_municipio = [
            cliente["cnpj"]
            for cliente in clientes
            if cliente.get("municipio", "").strip().upper() == municipio
        ]
        if cnpjs_do_municipio:
            plano.append((portal, cnpjs_do_municipio))

    return plano, municipios_sem_portal


def executar_rotina(caminho_csv: str | Path, pasta_destino: Path) -> None:
    clientes = ler_clientes_csv(caminho_csv)
    plano, municipios_sem_portal = montar_plano(clientes)

    if municipios_sem_portal:
        print(
            "Sem portal municipal configurado para: "
            + ", ".join(municipios_sem_portal)
            + " — CND municipal desses clientes fica de fora da rotina."
        )

    for portal, cnpjs in plano:
        print(f"\n=== {PORTAIS[portal]['nome']} ({len(cnpjs)} cliente(s)) ===")
        resultados = consultar_lista(cnpjs, pasta_destino, portal=portal)
        for resultado in resultados:
            print(linha_resumo(resultado))
