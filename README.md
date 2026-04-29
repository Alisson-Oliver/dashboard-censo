# Censo Curso Superior 2024 | Dashboard

Dashboard interativo desenvolvido com Streamlit para visualização e análise de dados do Censo da Educação Superior (INEP).

## Requisitos do Sistema

- **Python**: 3.8 ou superior
- **pip**: gerenciador de pacotes do Python
- **Git**: para clonar o repositório (opcional)

## Instalação

### Windows

#### 1. Clone ou baixe o projeto

```bash
git clone <repository-url>
cd dashboard-censo
```

#### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

#### 3. Ative o ambiente virtual

```bash
.venv\Scripts\activate
```

#### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

#### 5. Execute o dashboard

```bash
streamlit run Início.py
```

A aplicação será aberta automaticamente em `http://localhost:8501`.

### Linux / macOS

#### 1. Clone ou baixe o projeto

```bash
git clone <repository-url>
cd dashboard-censo
```

#### 2. Crie um ambiente virtual

```bash
python3 -m venv .venv
```

#### 3. Ative o ambiente virtual

```bash
source .venv/bin/activate
```

#### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

#### 5. Execute o dashboard

```bash
streamlit run Início.py
```

A aplicação será aberta automaticamente em `http://localhost:8501`.

## Estrutura do Projeto

```text
dashboard-censo/
├── Início.py
├── README.md
├── requirements.txt
├── data/
│   ├── data.csv
│   ├── dim_etnia.csv
│   └── brazil_states.geojson
├── pages/
│   ├── 5_Analise_INEP_e_Etnia.py
│   ├── 1_Visão_Geral_e_Distribuição_Geográfica.py
│   ├── 2_Fluxo_Acadêmico_e_Evolução.py
│   ├── 3_Perfil_Socioeconômico_do_Estudante.py
│   └── 4_Performance de Cursos e_Social.py
└── src/
    ├── __init__.py
    ├── database.py
    └── pages/
      ├── integrada_inep_etnia/
        ├── visao_geral/
        ├── fluxo_academico/
        ├── perfil_socioeconomico/
        └── performance_cursos/
```

## Arquitetura Técnica de Dados

### 1) Carregamento da base (ingestão)

O carregamento é centralizado em `src/database.py` por meio da classe `DatabaseConnection`.

Fluxo de inicialização:

1. Abre uma conexão DuckDB em memória (`duckdb.connect()`).
2. Resolve o caminho absoluto para `data/data.csv`.
3. Aplica `PRAGMA enable_object_cache` para melhorar reaproveitamento interno.
4. Carrega o CSV principal e a dimensão étnica uma única vez em tabelas temporárias:

```sql
CREATE OR REPLACE TEMP TABLE censo_data AS
SELECT *
FROM read_csv('.../data.csv', delim=';', encoding='latin-1')
```

```sql
CREATE OR REPLACE TEMP TABLE dim_etnia AS
SELECT *
FROM read_csv('.../dim_etnia.csv', delim=',', header=true)
```

Com isso, o arquivo não precisa ser relido para cada gráfico durante a mesma sessão.

### 2) Obtenção dos dados (queries)

As consultas são disparadas pelos módulos `business.py` de cada domínio em `src/pages/`:

- `src/pages/visao_geral/business.py`
- `src/pages/fluxo_academico/business.py`
- `src/pages/perfil_socioeconomico/business.py`
- `src/pages/performance_cursos/business.py`

Cada método do serviço executa agregações SQL (ex.: `SUM`, `COUNT`, `GROUP BY`, `CASE`) e retorna `DataFrame` pandas.

A análise integrada entre INEP e demografia fica em `src/pages/integrada_inep_etnia/` e faz o `JOIN` entre o censo e `dim_etnia` por UF/região, sempre agregando antes da renderização.

Detalhe importante de performance:

- Mesmo que a consulta do serviço use `FROM read_csv(...)`, a camada de banco reescreve automaticamente para `FROM censo_data` antes de executar.
- Essa reescrita é feita no método `_optimize_query`, reduzindo custo de I/O.

### 3) Organização da lógica

Separação por responsabilidade:

- `pages/*.py`: montagem da tela, seções, colunas e fluxo de interação.
- `src/pages/<dominio>/business.py`: regras de negócio e consultas.
- `src/pages/<dominio>/components.py`: criação dos gráficos Plotly.
- `src/database.py`: conexão, otimização e execução SQL.

Esse desenho facilita manutenção, testes e evolução de cada parte do dashboard.

### 4) Exibição dos dados (renderização)

O fluxo de exibição segue este padrão:

1. A página Streamlit chama métodos de `business.py`.
2. Recebe `DataFrame` com dados já agregados.
3. Passa os dados para `components.py`.
4. O componente monta o gráfico Plotly (`px.bar`, `px.pie`, `px.treemap`, etc.).
5. A página renderiza com `st.plotly_chart(..., use_container_width=True)`.

Resumo do pipeline:

`data/data.csv + data/dim_etnia.csv -> DuckDB (censo_data + dim_etnia) -> business.py -> DataFrame -> components.py -> Streamlit`

## Dados - INEP

Os dados utilizados neste projeto são provenientes do **Censo da Educação Superior** do INEP (Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira).

### Como Obter os Dados

1. Acesse o portal de dados abertos do INEP:
   https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior
2. Baixe o arquivo CSV do ano desejado (ex.: 2024).
3. Renomeie para `data.csv` (se necessário).
4. Coloque o arquivo em `data/data.csv`.

## Como Usar

1. Com o ambiente virtual ativo, execute:
   `streamlit run Início.py`
2. A página inicial será aberta em `Início.py`.
3. Navegue pelas páginas no menu lateral.
4. Interaja com filtros e gráficos para análise.

## Dependências

- **Streamlit**: interface web
- **DuckDB**: consultas SQL em alta performance
- **Plotly**: gráficos interativos
- **Pandas**: manipulação de dados

## Troubleshooting

**Erro ao ativar o ambiente virtual (Windows)?**

```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

**Erro ao instalar pacotes?**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Porta 8501 já está em uso?**

```bash
streamlit run Início.py --server.port 8502
```

## Notas

- Ative o ambiente virtual antes de executar o projeto.
- Garanta que `data/data.csv` existe.
- Configurações do Streamlit ficam em `.streamlit/config.toml`.
