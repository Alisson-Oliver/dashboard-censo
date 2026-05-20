from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


ROOT_DIR = Path(__file__).resolve().parents[3]
GEOJSON_PATH = ROOT_DIR / "data" / "brazil_states.geojson"

REGION_ORDER = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
DEMOGRAPHIC_COLUMNS = [
    ("PERC_BRANCA", "Pessoas brancas"),
    ("PERC_PRETA", "Pessoas pretas"),
    ("PERC_PARDA", "Pessoas pardas"),
    ("PERC_INDIGENA", "Pessoas indígenas"),
]


def _base_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=520,
        margin=dict(t=80, l=20, r=20, b=20),
        font=dict(family="Arial, sans-serif", size=13),
    )
    return fig


def render_scatter_preta_vs_matriculas(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df,
        x="PERC_PRETA",
        y="TOTAL_MATRICULAS",
        color="REGIAO",
        size="POP_TOTAL",
        hover_name="UF_NOME",
        custom_data=["UF", "UF_NOME", "REGIAO", "TOTAL_INGRESSANTES", "TOTAL_CONCLUINTES", "RENDA_MEDIA", "IDH", "ESCOLARIDADE_MEDIA"],
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={
            "PERC_PRETA": "% população preta",
            "TOTAL_MATRICULAS": "Total de matrículas",
            "REGIAO": "Região",
            "POP_TOTAL": "População total",
        },
        title="Relação entre percentual de pessoas pretas e matrículas no ensino superior",
    )
    fig.update_traces(
        marker=dict(opacity=0.86, line=dict(width=0.8, color="rgba(0,0,0,0.25)")),
        hovertemplate=(
            "<b>%{customdata[1]}</b><br>UF: %{customdata[0]}<br>Região: %{customdata[2]}"
            "<br>% preta: %{x:.1f}%<br>Matrículas: %{y:,.0f}"
            "<br>Ingressantes: %{customdata[3]:,.0f}<br>Concluintes: %{customdata[4]:,.0f}"
            "<br>Renda média: R$ %{customdata[5]:,.0f}<br>IDH: %{customdata[6]:.3f}"
            "<br>Escolaridade média: %{customdata[7]:.1f}"
            "<extra></extra>"
        ),
    )
    fig.update_layout(
        xaxis_title="Percentual de população preta",
        yaxis_title="Total de matrículas",
        legend_title_text="Região",
    )
    return _base_layout(fig, "Relação entre percentual de pessoas pretas e matrículas")


def render_modalidade_regional(df: pd.DataFrame) -> go.Figure:
    order = ["Presencial", "EAD", "Outro"]
    df = df.copy()
    df["TP_MODALIDADE_ENSINO"] = pd.Categorical(df["TP_MODALIDADE_ENSINO"], categories=order, ordered=True)
    fig = px.bar(
        df.sort_values(["REGIAO", "TP_MODALIDADE_ENSINO"]),
        x="REGIAO",
        y="TOTAL_MATRICULAS",
        color="TP_MODALIDADE_ENSINO",
        barmode="stack",
        text_auto=".2s",
        color_discrete_map={"Presencial": "#1d4ed8", "EAD": "#f59e0b", "Outro": "#94a3b8"},
        hover_data={"PERC_PARDA": ":.1f", "POP_TOTAL": ":,.0f"},
        labels={
            "REGIAO": "Região",
            "TOTAL_MATRICULAS": "Total de matrículas",
            "TP_MODALIDADE_ENSINO": "Modalidade",
            "PERC_PARDA": "% população parda",
            "POP_TOTAL": "População total",
        },
        title="Distribuição de modalidade de ensino por perfil regional",
    )
    fig.update_layout(xaxis_title="Região", yaxis_title="Total de matrículas", legend_title_text="Modalidade")
    return _base_layout(fig, "Distribuição de modalidade de ensino por perfil regional")


_ETNIA_COLORS = {
    "Branca": "#60a5fa",
    "Preta": "#1e293b",
    "Parda": "#d97706",
    "Indígena": "#16a34a",
    "Amarela": "#eab308",
}


def render_grafico_dinamico(
    df_long: pd.DataFrame,
    x_col: str,
    titulo: str,
    barmode: str = "group",
) -> go.Figure:
    """Gráfico de colunas com valor absoluto e rótulo de percentual.

    Parâmetros
    ----------
    df_long:
        DataFrame no formato longo com colunas:
        x_col, GRUPO_ETNICO, POPULACAO_EST, PERC_NO_TOTAL
    x_col:
        Coluna usada no eixo X ("UF_NOME" ou "REGIAO").
    titulo:
        Título exibido no gráfico.
    barmode:
        "group" (barras lado a lado) ou "stack" (barras empilhadas).
    """
    if df_long.empty:
        fig = go.Figure()
        fig.update_layout(
            title=titulo,
            template="plotly_white",
            annotations=[
                dict(
                    text="Nenhum dado para os filtros selecionados.",
                    x=0.5,
                    y=0.5,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="#94a3b8"),
                )
            ],
        )
        return fig

    grupos = df_long["GRUPO_ETNICO"].unique().tolist()
    x_values = df_long[x_col].unique().tolist()

    fig = go.Figure()

    for grupo in grupos:
        subset = df_long[df_long["GRUPO_ETNICO"] == grupo].copy()
        subset = subset.set_index(x_col).reindex(x_values).reset_index()

        pop_est = subset["POPULACAO_EST"].fillna(0).round(0)
        perc = subset["PERC_NO_TOTAL"].fillna(0)

        text_labels = [
            f"{int(v):,}".replace(",", ".") + f"<br>{p:.1f}%"
            for v, p in zip(pop_est, perc)
        ]

        fig.add_trace(
            go.Bar(
                name=grupo,
                x=subset[x_col],
                y=pop_est,
                text=text_labels,
                textposition="outside",
                textfont=dict(size=10),
                marker_color=_ETNIA_COLORS.get(grupo, "#94a3b8"),
                hovertemplate=(
                    f"<b>{grupo}</b><br>"
                    + "%{x}<br>"
                    + "Estimativa absoluta: %{y:,.0f}<br>"
                    + "% na população: %{customdata:.1f}%"
                    + "<extra></extra>"
                ),
                customdata=perc,
            )
        )

    fig.update_layout(
        title=titulo,
        template="plotly_white",
        barmode=barmode,
        height=560,
        margin=dict(t=90, l=20, r=20, b=60),
        font=dict(family="Arial, sans-serif", size=12),
        xaxis=dict(title=x_col.replace("UF_NOME", "Estado").replace("REGIAO", "Região"), tickangle=-20),
        yaxis=dict(title="Estimativa de pessoas (pop. × %)"),
        legend=dict(title="Autodeclaração", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        uniformtext=dict(mode="hide", minsize=8),
    )
    return fig


def render_choropleth_matriculas(df: pd.DataFrame) -> go.Figure:
    geojson = json.loads(GEOJSON_PATH.read_text(encoding="utf-8"))

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="UF",
        featureidkey="properties.sigla",
        color="TOTAL_MATRICULAS",
        color_continuous_scale="YlOrRd",
        hover_name="UF_NOME",
        hover_data={
            "UF": True,
            "REGIAO": True,
            "TOTAL_MATRICULAS": ":,.0f",
            "TOTAL_INGRESSANTES": ":,.0f",
            "TOTAL_CONCLUINTES": ":,.0f",
            "POP_TOTAL": ":,.0f",
            "PERC_PRETA": ":.1f",
            "PERC_PARDA": ":.1f",
            "IDH": ":.3f",
            "RENDA_MEDIA": ":,.0f",
            "ESCOLARIDADE_MEDIA": ":.1f",
        },
        labels={
            "TOTAL_MATRICULAS": "Total de matrículas",
            "TOTAL_INGRESSANTES": "Total de ingressantes",
            "TOTAL_CONCLUINTES": "Total de concluintes",
            "PERC_PRETA": "% população preta",
            "PERC_PARDA": "% população parda",
            "RENDA_MEDIA": "Renda média",
            "ESCOLARIDADE_MEDIA": "Escolaridade média",
        },
        title="Mapa choropleth do Brasil: matrículas por UF e indicadores sociais",
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_traces(
        marker_line_color="white",
        marker_line_width=0.8,
        hovertemplate=(
            "<b>%{hovertext}</b><br>UF: %{location}<br>Região: %{customdata[0]}"
            "<br>Matrículas: %{customdata[1]:,.0f}<br>Ingressantes: %{customdata[2]:,.0f}"
            "<br>Concluintes: %{customdata[3]:,.0f}<br>População total: %{customdata[4]:,.0f}"
            "<br>% preta: %{customdata[5]:.1f}%<br>% parda: %{customdata[6]:.1f}%"
            "<br>IDH: %{customdata[7]:.3f}<br>Renda média: R$ %{customdata[8]:,.0f}"
            "<br>Escolaridade média: %{customdata[9]:.1f}<extra></extra>"
        ),
        customdata=df[["REGIAO", "TOTAL_MATRICULAS", "TOTAL_INGRESSANTES", "TOTAL_CONCLUINTES", "POP_TOTAL", "PERC_PRETA", "PERC_PARDA", "IDH", "RENDA_MEDIA", "ESCOLARIDADE_MEDIA"]].to_numpy(),
    )
    fig.update_layout(
        geo=dict(scope="south america", projection_type="mercator"),
        margin=dict(t=80, l=20, r=20, b=20),
    )
    return _base_layout(fig, "Mapa choropleth das matrículas por UF")
