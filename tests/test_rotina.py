from consulta_cnd.rotina import montar_plano


def test_montar_plano_inclui_portais_para_toda_a_carteira():
    clientes = [
        {"cnpj": "111", "municipio": "CEU AZUL"},
        {"cnpj": "222", "municipio": "TOLEDO"},
    ]

    plano, _ = montar_plano(clientes)
    mapa = dict(plano)

    for portal in ("rfb", "cndt", "pr"):
        assert mapa[portal] == ["111", "222"]


def test_montar_plano_agrupa_por_municipio_conhecido_ignorando_maiusculas():
    clientes = [
        {"cnpj": "111", "municipio": "CEU AZUL"},
        {"cnpj": "222", "municipio": "Cascavel"},
        {"cnpj": "333", "municipio": "ceu azul"},
    ]

    plano, sem_portal = montar_plano(clientes)
    mapa = dict(plano)

    assert mapa["ceuazul-pr"] == ["111", "333"]
    assert mapa["cascavel-pr"] == ["222"]
    assert sem_portal == []


def test_montar_plano_reporta_municipios_sem_portal_configurado():
    clientes = [
        {"cnpj": "111", "municipio": "MEDIANEIRA"},
        {"cnpj": "222", "municipio": "FOZ DO IGUACU"},
    ]

    _, sem_portal = montar_plano(clientes)

    assert sem_portal == ["FOZ DO IGUACU", "MEDIANEIRA"]


def test_montar_plano_agrupa_toledo():
    clientes = [{"cnpj": "111", "municipio": "TOLEDO"}, {"cnpj": "222", "municipio": "CEU AZUL"}]

    plano, sem_portal = montar_plano(clientes)
    mapa = dict(plano)

    assert mapa["toledo-pr"] == ["111"]
    assert sem_portal == []


def test_montar_plano_agrupa_vera_cruz_do_oeste():
    clientes = [{"cnpj": "111", "municipio": "Vera Cruz do Oeste"}]

    plano, sem_portal = montar_plano(clientes)
    mapa = dict(plano)

    assert mapa["veracruzdooeste-pr"] == ["111"]
    assert sem_portal == []


def test_montar_plano_nao_gera_entrada_municipal_sem_clientes():
    clientes = [{"cnpj": "111", "municipio": "MEDIANEIRA"}]

    plano, _ = montar_plano(clientes)
    portais_no_plano = [portal for portal, _ in plano]

    assert "ceuazul-pr" not in portais_no_plano
    assert "cascavel-pr" not in portais_no_plano
    assert "toledo-pr" not in portais_no_plano
    assert "veracruzdooeste-pr" not in portais_no_plano
