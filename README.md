# Consulta CND — PERINAZZO CONTABILIDADE

Ferramenta interna para consultar a situação da Certidão Negativa de Débitos
(CND) — Receita Federal (RFB) e Procuradoria-Geral da Fazenda Nacional
(PGFN) — dos CNPJs da carteira de clientes.

Uso interno do escritório. Não distribuir fora da PERINAZZO CONTABILIDADE.

Há duas formas de consultar, no mesmo projeto:

1. **API oficial do SERPRO** (`consulta-cnd`) — 100% automatizada, requer
   contrato pago com o SERPRO.
2. **Portal público, semi-automática** (`consulta-cnd-navegador`) — gratuita,
   mas exige você resolver o CAPTCHA manualmente a cada CNPJ (o script só
   automatiza o preenchimento e a organização dos resultados).

## Opção 1 — API oficial do SERPRO

O projeto consome a **API oficial "Consulta CND" do SERPRO**, que é o canal
correto de automação total (em vez de fazer scraping do portal de emissão de
certidões, que tem CAPTCHA justamente para impedir acesso automatizado —
veja a Opção 2 abaixo para essa alternativa gratuita e sem contornar o
CAPTCHA).

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

### Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Uso

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

## Opção 2 — Consulta semi-automática pelo Portal de Serviços Digitais (gratuita)

Usa um navegador de verdade (Playwright) para abrir a página oficial de
consulta de CND no [Portal de Serviços Digitais da Receita Federal](https://servicos.receitafederal.gov.br/servico/certidoes/#/home/cnpj).

Esse portal **exige login com conta gov.br** (nível Prata ou Ouro) e é uma
aplicação de página única — por isso, diferente da Opção 1, aqui **login,
digitação do CNPJ e CAPTCHA são todos manuais**: o script abre a página
correta, você faz o login/consulta na janela do navegador, e quando o
resultado aparecer, pressiona Enter no terminal para o script seguir para o
próximo CNPJ, salvando o PDF baixado (se houver) e tentando identificar a
situação no texto da página.

Para não precisar logar no gov.br a cada execução, o navegador roda com um
**perfil persistente** (por padrão em `~/.consulta_cnd/perfil_navegador`,
fora do repositório — nunca é commitado). O login feito numa execução tende
a continuar valendo nas seguintes.

### Instalação

```bash
pip install -e ".[navegador]"
playwright install chromium
```

### Uso

```bash
consulta-cnd-navegador --arquivo clientes.csv
# ou
consulta-cnd-navegador --cnpj 11.222.333/0001-81
```

Os PDFs baixados vão para `./certidoes/<cnpj>.pdf` (pasta configurável com
`--pasta-destino`). Se a situação não for identificada automaticamente no
texto da página, a linha aparece como `DESCONHECIDA [CONFERIR PDF]` — abra o
PDF salvo para checar manualmente.

## Testes

```bash
pytest
```

Os testes cobrem validação de CNPJ, autenticação, o cliente da API e o
reconhecimento de situação do portal público — todos com chamadas HTTP
mockadas (ou apenas texto, no caso do portal), sem depender de credenciais
reais nem de navegador.

## Sigilo

Dados de clientes (CNPJ, situação fiscal) são confidenciais. Não usar CNPJs
reais em exemplos, testes ou issues — apenas os fictícios já presentes no
repositório.
