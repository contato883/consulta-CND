from consulta_cnd.models import ResultadoCertidao


def test_regular_para_negativa():
    assert ResultadoCertidao(cnpj="123", situacao="NEGATIVA").regular


def test_regular_para_positiva_com_efeito_de_negativa():
    assert ResultadoCertidao(cnpj="123", situacao="POSITIVA_COM_EFEITO_DE_NEGATIVA").regular


def test_regular_para_fgts_regular():
    assert ResultadoCertidao(cnpj="123", situacao="REGULAR").regular


def test_nao_regular_para_positiva():
    assert not ResultadoCertidao(cnpj="123", situacao="POSITIVA").regular


def test_nao_regular_para_fgts_irregular():
    assert not ResultadoCertidao(cnpj="123", situacao="IRREGULAR").regular


def test_nao_regular_para_desconhecida():
    assert not ResultadoCertidao(cnpj="123", situacao="DESCONHECIDA").regular
