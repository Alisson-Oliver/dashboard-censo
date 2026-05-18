"""
Pipeline ETL — Censo da Educação Superior

Etapas:
  1. Extract  — lê data/data.csv e data/dim_etnia.csv via DuckDB
  2. Validate — verifica colunas obrigatórias e avisa quando faltarem
  3. Transform — JOIN censo × etnia com agregações por UF, região e modalidade
  4. Load     — grava resultados em data/processed/*.parquet

O pipeline é chamado automaticamente por src/database.py na inicialização do
dashboard. Se os arquivos Parquet já existirem e forem mais novos que os CSVs
de origem, a execução é pulada (sem reprocessamento desnecessário).

Execução manual:
    python -m pipeline.etl           # pula se já atualizado
    python -m pipeline.etl --force   # força reprocessamento
"""

from __future__ import annotations

import logging
import os
import sys
import time

import duckdb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ETL] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE, "data")
_PROCESSED_DIR = os.path.join(_DATA_DIR, "processed")

CSV_CENSO = os.path.join(_DATA_DIR, "data.csv")
CSV_ETNIA_CANDIDATES = [
    os.path.join(_DATA_DIR, "dim_etnia.csv"),
    os.path.join(_DATA_DIR, "dados_demograficos_brasil_uf.csv"),
]

PARQUET_CENSO = os.path.join(_PROCESSED_DIR, "censo_agregado.parquet")
PARQUET_UF = os.path.join(_PROCESSED_DIR, "censo_etnia_uf.parquet")
PARQUET_REGIAO = os.path.join(_PROCESSED_DIR, "censo_etnia_regiao.parquet")
PARQUET_MODALIDADE = os.path.join(_PROCESSED_DIR, "censo_etnia_modalidade.parquet")

_ALL_OUTPUTS = [PARQUET_CENSO, PARQUET_UF, PARQUET_REGIAO, PARQUET_MODALIDADE]

# Colunas obrigatórias no CSV do censo (nomes canônicos do INEP)
_REQUIRED_CENSO_COLUMNS = {
    "SG_UF", "NO_UF", "NO_REGIAO", "CO_REGIAO",
    "TP_MODALIDADE_ENSINO", "QT_MAT", "QT_ING", "QT_CONC",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_etnia_path() -> str:
    for path in CSV_ETNIA_CANDIDATES:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"Arquivo de dimensão étnica não encontrado. "
        f"Esperado em: {CSV_ETNIA_CANDIDATES}"
    )


def _is_up_to_date() -> bool:
    """Retorna True se todos os Parquet existem e são mais novos que os CSVs."""
    if not all(os.path.exists(p) for p in _ALL_OUTPUTS):
        return False

    oldest_output = min(os.path.getmtime(p) for p in _ALL_OUTPUTS)

    source_files = [CSV_CENSO]
    try:
        source_files.append(_get_etnia_path())
    except FileNotFoundError:
        pass

    newest_source = max(
        (os.path.getmtime(f) for f in source_files if os.path.exists(f)),
        default=0,
    )

    return oldest_output >= newest_source


def _elapsed(start: float) -> str:
    return f"{time.time() - start:.2f}s"


# ---------------------------------------------------------------------------
# ETL Steps
# ---------------------------------------------------------------------------


def _extract(conn: duckdb.DuckDBPyConnection, etnia_path: str) -> None:
    """Carrega CSVs em tabelas temporárias DuckDB."""
    log.info("Extract: carregando data.csv …")
    conn.execute(
        f"""
        CREATE OR REPLACE TEMP TABLE raw_censo AS
        SELECT * FROM read_csv('{CSV_CENSO}', delim=';', encoding='latin-1')
        """
    )

    log.info("Extract: carregando dim_etnia …")
    conn.execute(
        f"""
        CREATE OR REPLACE TEMP TABLE raw_etnia AS
        SELECT * FROM read_csv('{etnia_path}', delim=',', header=true)
        """
    )


def _validate(conn: duckdb.DuckDBPyConnection) -> list[str]:
    """Verifica colunas obrigatórias; retorna lista de colunas ausentes."""
    rows = conn.execute("PRAGMA table_info('raw_censo')").fetchall()
    present = {row[1] for row in rows}
    missing = _REQUIRED_CENSO_COLUMNS - present

    if missing:
        log.warning(
            "Validate: colunas ausentes em data.csv: %s. "
            "Algumas agregações podem falhar.",
            sorted(missing),
        )
    else:
        log.info("Validate: todas as colunas obrigatórias encontradas.")

    return list(missing)


def _resolve_col(conn: duckdb.DuckDBPyConnection, table: str, candidates: list[str]) -> str:
    """Retorna o primeiro candidato que existe na tabela (case-insensitive)."""
    rows = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
    cols_lower = {row[1].lower(): row[1] for row in rows}
    for c in candidates:
        if c in {row[1] for row in rows}:
            return c
        if c.lower() in cols_lower:
            return cols_lower[c.lower()]
    raise KeyError(f"Nenhuma das colunas {candidates} encontrada em {table}")


def _transform_and_load(conn: duckdb.DuckDBPyConnection, missing_cols: list[str]) -> None:
    """Executa JOINs e agregações, salvando Parquet em data/processed/."""
    os.makedirs(_PROCESSED_DIR, exist_ok=True)

    # --- 1. Parquet bruto do censo (comprimido) ----------------------------
    t = time.time()
    log.info("Transform: salvando censo_agregado.parquet …")
    conn.execute(
        f"COPY raw_censo TO '{PARQUET_CENSO}' (FORMAT PARQUET, COMPRESSION SNAPPY)"
    )
    log.info("  → censo_agregado.parquet salvo em %s", _elapsed(t))

    # Resolve nomes de colunas dinamicamente (tolera variações do INEP)
    uf_col = _resolve_col(conn, "raw_censo", ["SG_UF", "UF"])
    uf_name_col = _resolve_col(conn, "raw_censo", ["NO_UF", "UF", "SG_UF"])
    regiao_col = _resolve_col(conn, "raw_censo", ["NO_REGIAO", "REGIAO"])
    co_regiao_col = _resolve_col(conn, "raw_censo", ["CO_REGIAO"])
    modalidade_col = _resolve_col(conn, "raw_censo", ["TP_MODALIDADE_ENSINO"])
    mat_col = _resolve_col(conn, "raw_censo", ["QT_MAT"])
    ing_col = _resolve_col(conn, "raw_censo", ["QT_ING"])
    conc_col = _resolve_col(conn, "raw_censo", ["QT_CONC"])

    def q(c: str) -> str:
        return f'"{c}"'

    # --- 2. censo_etnia_uf.parquet ----------------------------------------
    t = time.time()
    log.info("Transform: JOIN censo × etnia por UF …")
    conn.execute(
        f"""
        CREATE OR REPLACE TEMP TABLE censo_etnia_uf AS
        WITH censo_uf AS (
            SELECT
                {q(uf_col)}         AS UF,
                {q(uf_name_col)}    AS NO_UF,
                {q(regiao_col)}     AS REGIAO,
                {q(co_regiao_col)}  AS CO_REGIAO,
                SUM({q(mat_col)})   AS TOTAL_MATRICULAS,
                SUM({q(ing_col)})   AS TOTAL_INGRESSANTES,
                SUM({q(conc_col)})  AS TOTAL_CONCLUINTES
            FROM raw_censo
            GROUP BY 1, 2, 3, 4
        )
        SELECT
            c.UF,
            c.NO_UF,
            c.REGIAO,
            c.CO_REGIAO,
            c.TOTAL_MATRICULAS,
            c.TOTAL_INGRESSANTES,
            c.TOTAL_CONCLUINTES,
            d.POP_TOTAL,
            d.PERC_BRANCA,
            d.PERC_PRETA,
            d.PERC_PARDA,
            d.PERC_INDIGENA,
            d.PERC_AMARELA,
            d.RENDA_MEDIA,
            d.IDH,
            d.ESCOLARIDADE_MEDIA
        FROM censo_uf c
        LEFT JOIN raw_etnia d ON c.UF = d.UF
        ORDER BY c.TOTAL_MATRICULAS DESC
        """
    )
    conn.execute(
        f"COPY censo_etnia_uf TO '{PARQUET_UF}' (FORMAT PARQUET, COMPRESSION SNAPPY)"
    )
    log.info("  → censo_etnia_uf.parquet salvo em %s", _elapsed(t))

    # --- 3. censo_etnia_regiao.parquet ------------------------------------
    t = time.time()
    log.info("Transform: agregação por região …")
    conn.execute(
        f"""
        CREATE OR REPLACE TEMP TABLE censo_etnia_regiao AS
        WITH censo_regiao AS (
            SELECT
                {q(regiao_col)} AS REGIAO,
                SUM({q(mat_col)})  AS TOTAL_MATRICULAS,
                SUM({q(ing_col)})  AS TOTAL_INGRESSANTES,
                SUM({q(conc_col)}) AS TOTAL_CONCLUINTES
            FROM raw_censo
            GROUP BY 1
        ),
        etnia_regiao AS (
            SELECT
                REGIAO,
                SUM(POP_TOTAL) AS POP_TOTAL,
                SUM(POP_TOTAL * PERC_BRANCA)   / NULLIF(SUM(POP_TOTAL), 0) AS PERC_BRANCA,
                SUM(POP_TOTAL * PERC_PRETA)    / NULLIF(SUM(POP_TOTAL), 0) AS PERC_PRETA,
                SUM(POP_TOTAL * PERC_PARDA)    / NULLIF(SUM(POP_TOTAL), 0) AS PERC_PARDA,
                SUM(POP_TOTAL * PERC_INDIGENA) / NULLIF(SUM(POP_TOTAL), 0) AS PERC_INDIGENA
            FROM raw_etnia
            GROUP BY REGIAO
        )
        SELECT
            c.REGIAO,
            c.TOTAL_MATRICULAS,
            c.TOTAL_INGRESSANTES,
            c.TOTAL_CONCLUINTES,
            e.POP_TOTAL,
            e.PERC_BRANCA,
            e.PERC_PRETA,
            e.PERC_PARDA,
            e.PERC_INDIGENA,
            (c.TOTAL_MATRICULAS   / NULLIF(e.POP_TOTAL, 0)) * 100000 AS MATRICULAS_POR_100K,
            (c.TOTAL_INGRESSANTES / NULLIF(e.POP_TOTAL, 0)) * 100000 AS INGRESSANTES_POR_100K,
            (c.TOTAL_CONCLUINTES  / NULLIF(e.POP_TOTAL, 0)) * 100000 AS CONCLUINTES_POR_100K
        FROM censo_regiao c
        LEFT JOIN etnia_regiao e USING (REGIAO)
        ORDER BY MATRICULAS_POR_100K DESC
        """
    )
    conn.execute(
        f"COPY censo_etnia_regiao TO '{PARQUET_REGIAO}' (FORMAT PARQUET, COMPRESSION SNAPPY)"
    )
    log.info("  → censo_etnia_regiao.parquet salvo em %s", _elapsed(t))

    # --- 4. censo_etnia_modalidade.parquet --------------------------------
    t = time.time()
    log.info("Transform: agregação por modalidade × região …")
    conn.execute(
        f"""
        CREATE OR REPLACE TEMP TABLE censo_etnia_modalidade AS
        WITH censo_regiao AS (
            SELECT
                {q(regiao_col)} AS REGIAO,
                CASE
                    WHEN {q(modalidade_col)} = 2 THEN 'EAD'
                    WHEN {q(modalidade_col)} = 1 THEN 'Presencial'
                    ELSE 'Outro'
                END AS TP_MODALIDADE_ENSINO,
                SUM({q(mat_col)}) AS TOTAL_MATRICULAS
            FROM raw_censo
            GROUP BY 1, 2
        ),
        etnia_regiao AS (
            SELECT
                REGIAO,
                SUM(POP_TOTAL) AS POP_TOTAL,
                SUM(POP_TOTAL * PERC_PARDA) / NULLIF(SUM(POP_TOTAL), 0) AS PERC_PARDA
            FROM raw_etnia
            GROUP BY REGIAO
        )
        SELECT
            c.REGIAO,
            c.TP_MODALIDADE_ENSINO,
            c.TOTAL_MATRICULAS,
            e.POP_TOTAL,
            e.PERC_PARDA
        FROM censo_regiao c
        LEFT JOIN etnia_regiao e USING (REGIAO)
        ORDER BY c.REGIAO, c.TP_MODALIDADE_ENSINO
        """
    )
    conn.execute(
        f"COPY censo_etnia_modalidade TO '{PARQUET_MODALIDADE}' (FORMAT PARQUET, COMPRESSION SNAPPY)"
    )
    log.info("  → censo_etnia_modalidade.parquet salvo em %s", _elapsed(t))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_pipeline(force: bool = False) -> bool:
    """
    Executa o pipeline ETL.

    Parâmetros
    ----------
    force : bool
        Se True, reprocessa mesmo que os Parquet já estejam atualizados.

    Retorna
    -------
    bool
        True se o pipeline foi executado, False se foi pulado.
    """
    if not os.path.exists(CSV_CENSO):
        log.warning(
            "data/data.csv não encontrado — pipeline ETL ignorado. "
            "Baixe o arquivo do INEP e coloque em data/data.csv."
        )
        return False

    if not force and _is_up_to_date():
        log.info("Pipeline ETL: dados já atualizados, pulando reprocessamento.")
        return False

    total_start = time.time()
    log.info("=== Pipeline ETL iniciado ===")

    try:
        etnia_path = _get_etnia_path()
    except FileNotFoundError as exc:
        log.error("Pipeline ETL abortado: %s", exc)
        return False

    conn = duckdb.connect()
    try:
        conn.execute("PRAGMA threads=4")

        t = time.time()
        _extract(conn, etnia_path)
        log.info("Extract concluído em %s", _elapsed(t))

        missing_cols = _validate(conn)

        t = time.time()
        _transform_and_load(conn, missing_cols)
        log.info("Transform+Load concluído em %s", _elapsed(t))

    except Exception as exc:
        log.error("Pipeline ETL falhou: %s", exc, exc_info=True)
        return False
    finally:
        conn.close()

    log.info("=== Pipeline ETL finalizado em %s ===", _elapsed(total_start))
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    success = run_pipeline(force="--force" in sys.argv)
    sys.exit(0 if success is not False else 1)
