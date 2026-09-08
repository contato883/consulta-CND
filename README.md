# Consulta CND — PERINAZZO CONTABILIDADE

Ferramenta interna para consultar, de forma automatizada, a situação da Certidão
Negativa de Débitos (CND) — Receita Federal (RFB) e Procuradoria-Geral da
Fazenda Nacional (PGFN) — dos CNPJs da carteira de clientes.

Uso interno do escritório. Não distribuir fora da PERINAZZO CONTABILIDADE.

## Como funciona

O projeto consome a **API oficial "Consulta CND" do SERPRO**, que é o canal
correto e legal de automação (em vez de fazer scraping do portal de emissão
de certidões, que não é destinado a acesso automatizado).

- Autenticação: OAuth2 client credentials, via `POST https://gateway.apiserpro.serpro.gov.br/token`.
- Consulta: `POST https://gateway.apiserpro.serpro.gov.br/consulta-cnd-trial/v1/certidao` (ambiente trial) ou
  `.../consulta-cnd/v1/certidao` (produção).
- Documentação oficial: https://apicenter.estaleiro.serpro.gov.br/documentacao/consulta-cnd/
- Catálogo gov.br do serviço: https://www.gov.br/conecta/catalogo/apis/consultar-certidao-negativa-de-debito

**[A VERIFICAR]** — os nomes exatos dos campos do corpo da requisição e da
resposta (`_montar_payload` e `_interpretar_resposta` em
`src/consulta_cnd/client.py`) foram montados com base na documentação pública
da API, mas o schema completo (Swagger/OpenAPI) só é liberado no Client Area
do SERPRO após a contratação do serviço. Antes de usar em produção, confira o
Swagger do contrato e ajuste esses dois métodos se os campos divergirem.

## Contratação e credenciais

1. Contratar o serviço "Consulta CND" no [Portal SERPRO](https://loja.serpro.gov.br/)
   (há ambiente trial gratuito para homologação e ambiente de produção pago).
2. No Client Area do SERPRO, gerar **Consumer Key** e **Consumer Secret**.
3. Copiar `.env.example` para `.env` e preencher:

   ```
   SERPRO_CONSUMER_KEY=xxxx
   SERPRO_CONSUMER_SECRET=xxxx
   SERPRO_AMBIENTE=trial   # ou "producao"
   ```

Nunca commitar o arquivo `.env` nem CNPJs reais de clientes — veja `.gitignore`.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

Consultar um ou mais CNPJs diretamente:

```bash
export $(cat .env | xargs)
consulta-cnd --cnpj 11.222.333/0001-81 --cnpj 12345678000195
```

Consultar a partir de uma planilha CSV com coluna `cnpj` (veja
`exemplos/clientes.exemplo.csv`):

```bash
consulta-cnd --arquivo clientes.csv
```

Saída (uma linha por CNPJ):

```
11.222.333/0001-81  NEGATIVA                       [OK]
12.345.678/0001-95  POSITIVA                       [PENDÊNCIA]
```

## Testes

```bash
pytest
```

Os testes cobrem validação de CNPJ, autenticação e o cliente da API — todos
com chamadas HTTP mockadas, sem depender de credenciais reais.

## Sigilo

Dados de clientes (CNPJ, situação fiscal) são confidenciais. Não usar CNPJs
reais em exemplos, testes ou issues — apenas os fictícios já presentes no
repositório.
