# Censo Curso Superior 2024 | Dashboard

Dashboard interativo desenvolvido com Streamlit para visualização e análise de dados do Censo de Educação Superior 2024 do INEP.

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

A aplicação será aberta automaticamente em `http://localhost:8501`

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
streamlit run app.py
```

A aplicação será aberta automaticamente em `http://localhost:8501`

## Estrutura do Projeto

```
dashboard-censo/
├── app.py                      # Página principal do dashboard
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
├── data/
│   └── data.csv               # Dados do Censo em formato CSV
├── pages/
│   ├── 01_Pagina1.py          # Primeira página (Streamlit multi-page)
│   └── 02_Pagina2.py          # Segunda página (Streamlit multi-page)
├── src/
│   ├── business.py            # Lógica de negócio e processamento de dados
│   ├── components.py          # Componentes Streamlit reutilizáveis
│   └── database.py            # Funções de acesso e conexão com dados
├── .streamlit/                # Configurações do Streamlit
└── .venv/                     # Ambiente virtual Python (criado automaticamente)
```

### Descrição dos Arquivos

| Arquivo/Pasta         | Descrição                                                         |
| --------------------- | ----------------------------------------------------------------- |
| **app.py**            | Página principal da aplicação Streamlit com configurações globais |
| **pages/**            | Diretório com páginas adicionais (multi-page app)                 |
| **src/business.py**   | Funções de lógica de negócio e processamento                      |
| **src/components.py** | Componentes e widgets reutilizáveis da interface                  |
| **src/database.py**   | Funções para leitura e manipulação de dados                       |
| **data/data.csv**     | Arquivo de dados do Censo em CSV                                  |
| **requirements.txt**  | Lista de dependências Python                                      |

## Dependências

- **Streamlit** ^1.0 - Framework para criar aplicações web em Python
- **DuckDB** - Banco de dados SQL rápido e eficiente
- **Plotly** - Biblioteca para visualizações interativas
- **Pandas** - Manipulação e análise de dados

## Dados - INEP

Os dados utilizados neste projeto são provenientes do **Censo da Educação Superior 2024** do INEP (Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira).

### Como Obter os Dados

1. Acesse o portal de dados abertos do INEP:
   - https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior

2. Na página, procure por **"2024"** na seção de Microdados

3. Baixe o arquivo **CSV** do Censo de 2024

4. Renomeie o arquivo para `data.csv` (se necessário)

5. Coloque o arquivo no diretório `data/` do projeto:

   ```
   dashboard-censo/
   ├── data/
   │   └── data.csv  ← Arquivo baixado aqui
   ```

6. Agora você pode executar o dashboard normalmente:
   ```bash
   streamlit run app.py
   ```

## Como Usar

1. Após obter os dados e colocá-los em `data/data.csv`, execute: `streamlit run app.py`
2. A página principal será aberta em `app.py`
3. Use o menu lateral para navegar entre as diferentes páginas
4. Os dados são carregados automaticamente do arquivo `data/data.csv`
5. Interaja com os gráficos e filtros conforme necessário

## Desenvolvimento

Para adicionar novas páginas:

1. Crie um novo arquivo em `pages/` com o padrão `NN_NomePagina.py`
2. Importe e use componentes de `src/components.py`
3. Use funções de `src/business.py` para lógica de negócio

## Troubleshooting

**Erro ao ativar o ambiente virtual (Windows)?**

```bash
# Se receber erro de permissão, execute como administrador ou use:
python -m venv .venv
.venv\Scripts\activate.bat
```

**Erro ao instalar pacotes?**

```bash
# Atualize o pip primeiro:
pip install --upgrade pip
pip install -r requirements.txt
```

**Porta 8501 já está em uso?**

```bash
streamlit run app.py --server.port 8502
```

## Notas

- O ambiente virtual deve ser ativado antes de executar o projeto
- Certifique-se de que todos os arquivos de dados estão no diretório `data/`
- A configuração do Streamlit está em `.streamlit/config.toml`
