## Atividade 2 - Pipeline ETL para API de Universidades

### Integrantes do Grupo

- Gabriel Moraes da Silva
- Cauã Otaviano Jordão
- Victor Barbosa

## Objetivo

Desenvolver um pipeline ETL (Extract, Transform, Load) que extrai dados de universidades de uma API pública e persiste em banco de dados relacional SQLite, aplicando boas práticas de desenvolvimento Python.

## Descrição do Projeto

Este projeto consome a API pública [Universities Hipolabs](http://universities.hipolabs.com) para extrair informações sobre universidades de diferentes países e armazená-las em um banco de dados SQLite utilizando SQLAlchemy ORM.

A API retorna dados no formato:

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

## Implementação Realizada

### Arquitetura em Camadas

O projeto foi estruturado seguindo o padrão de camadas, separando responsabilidades entre extração, carregamento e inicialização do banco:

#### 1. Camada de Inicialização (`db_init.py`)

Define os modelos SQLAlchemy que mapeiam a estrutura do banco de dados:

- **Country**: Armazena países com código ISO2
- **University**: Entidade principal com nome, país e estado/província
- **UniversityDomain**: Domínios associados às universidades (relacionamento 1:N)
- **UniversityWebPage**: Páginas web das universidades (relacionamento 1:N)

**Características implementadas:**
- Constraints únicas para evitar duplicação de dados
- Índices em `country_id`, `name`, `domain` e `url` para otimizar consultas
- Relacionamentos bidirecionais com cascade para manutenção de integridade

#### 2. Camada de Extração (`src/extract.py`)

Classe `UniversityExtractor` responsável por acessar a API e desserializar dados JSON.

**Funcionalidades principais:**

- `fetch_by_country(country: str)`: Busca universidades de um país específico
- `fetch_by_countries(countries: Iterable[str])`: Busca universidades de múltiplos países

**Recursos implementados:**
- Timeout configurável (padrão: 30s)
- Validação de respostas HTTP com `raise_for_status()`
- Type hints completos
- Docstrings descritivas em português

#### 3. Camada de Carregamento (`src/load.py`)

Classe `UniversityLoader` responsável por persistir dados no banco.

**Funcionalidades principais:**

- `load(universities: list[dict])`: Persiste universidades e retorna quantidade inserida
- Evita duplicações verificando existência antes de inserir
- Gerencia transações com commit único ao final

**Estratégia de persistência:**
1. Busca ou cria o país baseado no código ISO2
2. Verifica se universidade já existe (country_id, name, state_province)
3. Insere universidade, domínios e páginas web
4. Commit transacional único

#### 4. Script Principal (`main.py`)

Orquestra a execução do pipeline ETL:

```python
countries = ["Brazil", "Argentina", "Chile"]
extractor = UniversityExtractor()
loader = UniversityLoader()
universities = extractor.fetch_by_countries(countries)
inserted = loader.load(universities)
```

### Modelagem do Banco de Dados

A modelagem utiliza SQLAlchemy ORM com SQLite:

**Tabela `country`:**
- `id` (PK), `iso2` (UNIQUE), `name`

**Tabela `university`:**
- `id` (PK), `country_id` (FK), `name`, `state_province`
- Constraint única: `(country_id, name, state_province)`
- Índices: `country_id`, `name`

**Tabela `university_domain`:**
- `id` (PK), `university_id` (FK), `domain`
- Constraint única: `(university_id, domain)`
- Índice: `domain`

**Tabela `university_webpage`:**
- `id` (PK), `university_id` (FK), `url`
- Constraint única: `(university_id, url)`
- Índice: `url`

## Boas Práticas Implementadas

De acordo com os requisitos da atividade, foram aplicadas as seguintes boas práticas:

### ✅ Docstrings

Todos os métodos desenvolvidos contêm docstrings descritivas em português:

```python
def fetch_by_country(self, country: str) -> list[dict]:
    """Busca universidades de um unico pais."""
```

### ✅ Type Hints

Uso consistente de anotações de tipo para melhor legibilidade e detecção de erros:

```python
def load(self, universities: list[dict]) -> int:
```

### ✅ Formatação com Black

O projeto utiliza Black para garantir formatação consistente do código:

```bash
black .
```

### ✅ Separação de Responsabilidades

- **Extração**: `src/extract.py`
- **Carregamento**: `src/load.py`
- **Modelos**: `db_init.py`
- **Orquestração**: `main.py`

### ✅ Idempotência

O sistema verifica duplicados antes de inserir, permitindo execuções repetidas sem duplicação de dados.

### ✅ Tratamento de Erros

Validação adequada de respostas HTTP com `raise_for_status()`.

## Como Executar

### Pré-requisitos

- Python 3.10+
- pip

### Instalação e Execução

#### Linux / macOS

```bash
# 1. Crie o ambiente virtual
python3 -m venv .venv

# 2. Ative o ambiente virtual
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. (Opcional) Formate o código
black .

# 5. Execute o pipeline ETL
python main.py
```

#### Windows (PowerShell)

```powershell
# 1. Crie o ambiente virtual
python -m venv .venv

# 2. Ative o ambiente virtual
.\.venv\Scripts\Activate.ps1

# 3. Instale as dependências
pip install -r requirements.txt

# 4. (Opcional) Formate o código
black .

# 5. Execute o pipeline ETL
python main.py
```

### Saída Esperada

```
Universidades inseridas: 150
```

O arquivo `unis.db` será criado na raiz do projeto contendo os dados extraídos.

## Estrutura do Projeto

```
cesar-engenharia-dados/
├── src/
│   ├── __init__.py
│   ├── extract.py          # Camada de extração da API
│   └── load.py             # Camada de carregamento no banco
├── docs/
│   └── atividade 2/
│       └── README.md       # Este documento
├── db_init.py              # Modelos SQLAlchemy e configuração do banco
├── main.py                 # Script principal do pipeline ETL
├── requirements.txt        # Dependências do projeto
├── schema.sql              # Schema SQL (referência)
├── .gitignore              # Arquivos ignorados pelo Git
└── unis.db                 # Banco de dados SQLite (gerado após execução)
```

## Dependências

O projeto utiliza as seguintes bibliotecas (listadas em `requirements.txt`):

- **requests**: Requisições HTTP para consumir a API
- **sqlalchemy**: ORM para interação com banco de dados
- **black**: Formatador de código Python

## Observações

- O ambiente virtual (`.venv`) **não** foi incluído no repositório Git, conforme boas práticas
- O banco de dados SQLite (`unis.db`) é gerado automaticamente na primeira execução
- A implementação garante idempotência: execuções repetidas não duplicam dados
- Todos os métodos seguem o padrão de documentação com docstrings e type hints
