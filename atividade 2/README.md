# Persistência Relacional dos Dados da API de Universidades

## Contexto

Foi extraído um arquivo **JSON a partir de uma API de universidades**.  
O objetivo agora é **persistir esses dados em um banco de dados relacional** para permitir:

- consultas futuras
- manutenção de histórico
- integração com outras aplicações

A API retorna dados no formato semelhante a:

```json
{
  "name": "Universidade Federal de São Paulo",
  "country": "Brazil",
  "alpha_two_code": "BR",
  "state-province": null,
  "domains": ["epm.br"],
  "web_pages": ["http://www.epm.br/"]
}
```

Cada universidade possui:

- nome 
- país 
- código ISO do país 
- estado/província (opcional)
- lista de domínios 
- lista de páginas web

## Modelagem do Banco de Dados

A modelagem relacional proposta separa os dados em quatro tabelas principais, seguindo princípios de normalização e integridade referencial.

### Estrutura das Tabelas

Tabela `country`

Armazena os países de forma padronizada.

```sql
CREATE TABLE country (
     id           BIGSERIAL PRIMARY KEY,
     iso2         CHAR(2) NOT NULL UNIQUE,
     name         VARCHAR(120) NOT NULL
);
```

Motivação:

- Evita repetição do nome do país em todas as universidades 
- Garante padronização com código ISO (BR, US, etc.)
- Facilita consultas por país

Tabela `university`

Representa a entidade principal retornada pela API.

```sql
CREATE TABLE university (
    id               BIGSERIAL PRIMARY KEY,
    country_id       BIGINT NOT NULL,
    name             VARCHAR(300) NOT NULL,
    state_province   VARCHAR(120),

    CONSTRAINT uk_university UNIQUE (country_id, name, state_province),
    CONSTRAINT fk_university_country FOREIGN KEY (country_id) REFERENCES country(id)
);
```
Características importantes:

- `Country_id` cria relacionamento com a tabela `country` 
- `State_province` é opcional 
- `uk_university` evita duplicação da mesma universidade em cargas repetidas

Índices auxiliares:

```sql
CREATE INDEX ix_university_country ON university(country_id);
CREATE INDEX ix_university_name ON university(name);
```

Esses índices melhoram:

- Consultas por país 
- Buscas por nome

Tabela `university_domain`

Armazena os domínios associados às universidades.

```sql
CREATE TABLE university_domain (
   id            BIGSERIAL PRIMARY KEY,
   university_id BIGINT NOT NULL,
   domain        VARCHAR(253) NOT NULL,

   CONSTRAINT uk_university_domain UNIQUE (university_id, domain),
   CONSTRAINT fk_domain_university FOREIGN KEY (university_id) REFERENCES university(id)
);
```

Características:

- uma universidade pode ter vários domínios

- Relacionamento 1:N

- `uk_university_domain` evita domínios duplicados

Índice:

```sql
CREATE INDEX ix_domain_domain ON university_domain(domain);
```

Tabela `university_webpage`

Armazena as páginas web associadas às universidades.

```sql
CREATE TABLE university_webpage (
    id            BIGSERIAL PRIMARY KEY,
    university_id BIGINT NOT NULL,
    url           VARCHAR(2048) NOT NULL,

    CONSTRAINT uk_university_webpage UNIQUE (university_id, url),
    CONSTRAINT fk_webpage_university FOREIGN KEY (university_id) REFERENCES university(id)
);
```

Características:

- Uma universidade pode ter várias páginas web

- Relacionamento 1:N

- Constraint evita duplicação

Índice:

```sql
CREATE INDEX ix_webpage_url ON university_webpage(url);
```

## Estratégia para salvar dados de vários país

Quando a API retorna universidades de múltiplos países, é necessário garantir:

* consistência

* bom desempenho

* facilidade de manutenção

A estratégia adotada combina normalização, controle de duplicidade e processamento em lotes.

### 1. Processamento por país

Uma abordagem recomendada é importar os dados país por país.

Exemplo:

1. Buscar universidades do Brasil
2. Persistir no banco
3. Buscar universidades do Canadá
4. Persistir no banco

Benefícios:

* menor volume por transação
* facilita reprocessamento
* facilita rastreamento de erros

## 2. Uso de chaves únicas (idempotência)

A importação pode ocorrer várias vezes sem duplicar registros.

Isso é garantido pelas constraints:

* `country.iso2 UNIQUE`
* `uk_university (country_id, name, state_province)`
* `uk_university_domain (university_id, domain)`
* `uk_university_webpage (university_id, url)`

Assim, mesmo que a API retorne os mesmos dados novamente, o banco não criará duplicações.

###  3. Estratégia de UPSERT

A inserção deve utilizar uma estratégia de UPSERT.

Exemplo no PostgreSQL:

```sql
INSERT INTO university (...)
ON CONFLICT (...) DO NOTHING;
```

OU

```sql
INSERT INTO university (...)
ON CONFLICT (...) DO UPDATE ...
```

Isso permite que:

* novos registros sejam inseridos
* registros existentes sejam ignorados ou atualizados

### 4. Uso de índices

Os índices definidos garantem boa performance de consulta, especialmente em cenários com muitos registros.

Principais índices:

* ix_university_country
* ix_university_name
* ix_domain_domain
* ix_webpage_url

Eles permitem consultas rápidas como:

* universidades por país
* busca por domínio
* busca por nome

5. Facilidade de manutenção

A modelagem adotada facilita manutenção porque:

* evita redundância de dados
* separa entidades principais de listas
* garante integridade referencial via chaves estrangeiras
* permite expansão futura do modelo

Por exemplo, seria fácil adicionar:

* ranking de universidades
* localização geográfica
* dados históricos

## Exemplo de consulta

```sql
SELECT
    u.name,
    c.name AS country,
    d.domain,
    w.url
FROM university u
         JOIN country c ON c.id = u.country_id
         LEFT JOIN university_domain d ON d.university_id = u.id
         LEFT JOIN university_webpage w ON w.university_id = u.id
WHERE c.iso2 = 'BR'
ORDER BY u.name;
```