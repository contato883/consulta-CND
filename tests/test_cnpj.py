from consulta_cnd.cnpj import cnpj_valido, formatar_cnpj, limpar_cnpj

CNPJ_FICTICIO_VALIDO = "11.222.333/0001-81"


def test_limpar_cnpj_remove_mascara():
    assert limpar_cnpj(CNPJ_FICTICIO_VALIDO) == "11222333000181"


def test_cnpj_valido_aceita_com_e_sem_mascara():
    assert cnpj_valido(CNPJ_FICTICIO_VALIDO)
    assert cnpj_valido("11222333000181")


def test_cnpj_valido_rejeita_digito_verificador_errado():
    assert not cnpj_valido("11.222.333/0001-80")


def test_cnpj_valido_rejeita_digitos_repetidos():
    assert not cnpj_valido("11111111111111")


def test_cnpj_valido_rejeita_tamanho_errado():
    assert not cnpj_valido("123")


def test_formatar_cnpj():
    assert formatar_cnpj("11222333000181") == CNPJ_FICTICIO_VALIDO
