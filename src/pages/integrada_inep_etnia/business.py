from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from src.database import get_db


@dataclass(frozen=True)
class ColumnMap:
    uf_code: str
    uf_name: str
    region_name: str
    region_code: str | None
    modality: str
    matriculas: str
    ingressantes: str
    concluintes: str


UF_TO_NAME = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}


def _resolve_column_map() -> ColumnMap:
    db = get_db()
    return ColumnMap(
        uf_code=db.resolve_column("censo_data", ["SG_UF", "UF", "NO_UF"]),
        uf_name=db.resolve_column("censo_data", ["NO_UF", "UF", "SG_UF"]),
        region_name=db.resolve_column("censo_data", ["NO_REGIAO", "REGIAO"]),
        region_code=db.resolve_column("censo_data", ["CO_REGIAO"]),
        modality=db.resolve_column("censo_data", ["TP_MODALIDADE_ENSINO"]),
        matriculas=db.resolve_column("censo_data", ["QT_MAT"]),
        ingressantes=db.resolve_column("censo_data", ["QT_ING"]),
        concluintes=db.resolve_column("censo_data", ["QT_CONC"]),
    )


def _quoted(column_name: str) -> str:
    return f'"{column_name}"'


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame]:
    """Carrega as bases já agregadas em DuckDB antes da renderização."""
    db = get_db()
    columns = _resolve_column_map()

    censo_uf_query = f"""
    WITH censo_uf AS (
        SELECT
            {_quoted(columns.uf_code)} AS UF,
            {_quoted(columns.uf_name)} AS NO_UF,
            {_quoted(columns.region_name)} AS REGIAO,
            {_quoted(columns.region_code)} AS CO_REGIAO,
            SUM({_quoted(columns.matriculas)}) AS TOTAL_MATRICULAS,
            SUM({_quoted(columns.ingressantes)}) AS TOTAL_INGRESSANTES,
            SUM({_quoted(columns.concluintes)}) AS TOTAL_CONCLUINTES
        FROM censo_data
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
    LEFT JOIN dim_etnia d
        ON c.UF = d.UF
    ORDER BY c.TOTAL_MATRICULAS DESC
    """

    modalidade_query = f"""
    WITH censo_regiao AS (
        SELECT
            {_quoted(columns.region_name)} AS REGIAO,
            CASE
                WHEN {_quoted(columns.modality)} = 2 THEN 'EAD'
                WHEN {_quoted(columns.modality)} = 1 THEN 'Presencial'
                ELSE 'Outro'
            END AS TP_MODALIDADE_ENSINO,
            SUM({_quoted(columns.matriculas)}) AS TOTAL_MATRICULAS
        FROM censo_data
        GROUP BY 1, 2
    ),
    etnia_regiao AS (
        SELECT
            REGIAO,
            SUM(POP_TOTAL) AS POP_TOTAL,
            SUM(POP_TOTAL * PERC_PARDA) / NULLIF(SUM(POP_TOTAL), 0) AS PERC_PARDA
        FROM dim_etnia
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

    region_query = f"""
    WITH censo_regiao AS (
        SELECT
            {_quoted(columns.region_name)} AS REGIAO,
            SUM({_quoted(columns.matriculas)}) AS TOTAL_MATRICULAS,
            SUM({_quoted(columns.ingressantes)}) AS TOTAL_INGRESSANTES,
            SUM({_quoted(columns.concluintes)}) AS TOTAL_CONCLUINTES
        FROM censo_data
        GROUP BY 1
    ),
    etnia_regiao AS (
        SELECT
            REGIAO,
            SUM(POP_TOTAL) AS POP_TOTAL,
            SUM(POP_TOTAL * PERC_BRANCA) / NULLIF(SUM(POP_TOTAL), 0) AS PERC_BRANCA,
            SUM(POP_TOTAL * PERC_PRETA) / NULLIF(SUM(POP_TOTAL), 0) AS PERC_PRETA,
            SUM(POP_TOTAL * PERC_PARDA) / NULLIF(SUM(POP_TOTAL), 0) AS PERC_PARDA,
            SUM(POP_TOTAL * PERC_INDIGENA) / NULLIF(SUM(POP_TOTAL), 0) AS PERC_INDIGENA
        FROM dim_etnia
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
        (c.TOTAL_MATRICULAS / NULLIF(e.POP_TOTAL, 0)) * 100000 AS MATRICULAS_POR_100K,
        (c.TOTAL_INGRESSANTES / NULLIF(e.POP_TOTAL, 0)) * 100000 AS INGRESSANTES_POR_100K,
        (c.TOTAL_CONCLUINTES / NULLIF(e.POP_TOTAL, 0)) * 100000 AS CONCLUINTES_POR_100K
    FROM censo_regiao c
    LEFT JOIN etnia_regiao e USING (REGIAO)
    ORDER BY MATRICULAS_POR_100K DESC
    """

    return {
        "uf": db.execute_query(censo_uf_query).df(),
        "modalidade": db.execute_query(modalidade_query).df(),
        "regiao": db.execute_query(region_query).df(),
    }


def transform_data(raw_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Normaliza a saída agregada para cada visualização específica."""
    uf_df = raw_data["uf"].copy()
    modalidade_df = raw_data["modalidade"].copy()
    regiao_df = raw_data["regiao"].copy()

    uf_df["UF_NOME"] = uf_df["UF"].map(UF_TO_NAME).fillna(uf_df["NO_UF"])

    uf_df["MATRICULAS_POR_100K"] = (uf_df["TOTAL_MATRICULAS"] / uf_df["POP_TOTAL"]) * 100000
    uf_df["INGRESSANTES_POR_100K"] = (uf_df["TOTAL_INGRESSANTES"] / uf_df["POP_TOTAL"]) * 100000
    uf_df["CONCLUINTES_POR_100K"] = (uf_df["TOTAL_CONCLUINTES"] / uf_df["POP_TOTAL"]) * 100000

    regiao_df["REGIAO"] = pd.Categorical(
        regiao_df["REGIAO"],
        categories=["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"],
        ordered=True,
    )
    regiao_df = regiao_df.sort_values("REGIAO")

    return {
        "uf": uf_df,
        "modalidade": modalidade_df,
        "regiao": regiao_df,
    }


def create_kpis(data: dict[str, pd.DataFrame]) -> dict[str, object]:
    """Calcula KPIs a partir das bases já agregadas e relacionadas."""
    uf_df = data["uf"]
    regiao_df = data["regiao"]

    region_access = regiao_df.sort_values("MATRICULAS_POR_100K", ascending=False).iloc[0]
    state_concentration = uf_df.sort_values("TOTAL_MATRICULAS", ascending=False).iloc[0]

    return {
        "total_matriculas": int(uf_df["TOTAL_MATRICULAS"].sum()),
        "total_ingressantes": int(uf_df["TOTAL_INGRESSANTES"].sum()),
        "total_concluintes": int(uf_df["TOTAL_CONCLUINTES"].sum()),
        "regiao_maior_acesso": str(region_access["REGIAO"]),
        "taxa_acesso_regiao": float(region_access["MATRICULAS_POR_100K"]),
        "estado_maior_concentracao": str(state_concentration["UF_NOME"]),
        "estado_maior_concentracao_sigla": str(state_concentration["UF"]),
    }


GRUPOS_ETNICOS = {
    "Branca": "PERC_BRANCA",
    "Preta": "PERC_PRETA",
    "Parda": "PERC_PARDA",
    "Indígena": "PERC_INDIGENA",
    "Amarela": "PERC_AMARELA",
}


def get_etnia_dinamica(uf_df: pd.DataFrame) -> pd.DataFrame:
    """Expande as colunas PERC_* em linhas para uso no gráfico dinâmico.

    Retorna DataFrame com colunas:
        UF, UF_NOME, REGIAO, GRUPO_ETNICO, POPULACAO_EST, PERC_NO_TOTAL
    onde POPULACAO_EST é a estimativa absoluta de pessoas por grupo étnico
    e PERC_NO_TOTAL é o percentual daquele grupo na população total da UF.
    """
    rows = []
    for _, row in uf_df.iterrows():
        raw_pop = row.get("POP_TOTAL")
        pop_total = 0.0 if pd.isna(raw_pop) else float(raw_pop)
        for grupo, col in GRUPOS_ETNICOS.items():
            raw_perc = row.get(col)
            perc = 0.0 if pd.isna(raw_perc) else float(raw_perc)
            pop_est = pop_total * perc / 100.0
            rows.append(
                {
                    "UF": row["UF"],
                    "UF_NOME": row["UF_NOME"],
                    "REGIAO": row["REGIAO"],
                    "GRUPO_ETNICO": grupo,
                    "POPULACAO_EST": pop_est,
                    "PERC_NO_TOTAL": perc,
                }
            )
    return pd.DataFrame(rows)


def create_charts(data: dict[str, pd.DataFrame]) -> dict[str, object]:
    """Constrói os objetos Plotly a partir das tabelas transformadas."""
    from src.pages.integrada_inep_etnia import components

    return {
        "scatter": components.render_scatter_preta_vs_matriculas(data["uf"]),
        "modalidade": components.render_modalidade_regional(data["modalidade"]),
        "mapa": components.render_choropleth_matriculas(data["uf"]),
    }
