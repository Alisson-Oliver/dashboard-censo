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


def render_heatmap_acesso(df: pd.DataFrame) -> go.Figure:
    matrix_ingressantes = []
    matrix_concluintes = []
    hover_ingressantes = []
    hover_concluintes = []

    for _, row in df.iterrows():
        row_ing = []
        row_conc = []
        row_hover_ing = []
        row_hover_conc = []
        for column, label in DEMOGRAPHIC_COLUMNS:
            share = float(row[column]) if pd.notna(row[column]) else 0.0
            ing_value = float(row["TOTAL_INGRESSANTES"]) * share / 100.0
            conc_value = float(row["TOTAL_CONCLUINTES"]) * share / 100.0
            row_ing.append(ing_value)
            row_conc.append(conc_value)
            row_hover_ing.append(f"{label}<br>Share: {share:.1f}%<br>Ponderado: {ing_value:,.0f}")
            row_hover_conc.append(f"{label}<br>Share: {share:.1f}%<br>Ponderado: {conc_value:,.0f}")
        matrix_ingressantes.append(row_ing)
        matrix_concluintes.append(row_conc)
        hover_ingressantes.append(row_hover_ing)
        hover_concluintes.append(row_hover_conc)

    region_labels = df["REGIAO"].tolist()
    indicator_labels = [label for _, label in DEMOGRAPHIC_COLUMNS]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Ingressantes ponderados pela composição demográfica", "Concluintes ponderados pela composição demográfica"),
        horizontal_spacing=0.08,
    )

    fig.add_trace(
        go.Heatmap(
            z=np.array(matrix_ingressantes),
            x=indicator_labels,
            y=region_labels,
            colorscale="Blues",
            colorbar=dict(title="Ingressantes"),
            hovertemplate="Região: %{y}<br>%{customdata}<br>Valor: %{z:,.0f}<extra></extra>",
            customdata=np.array(hover_ingressantes),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Heatmap(
            z=np.array(matrix_concluintes),
            x=indicator_labels,
            y=region_labels,
            colorscale="Oranges",
            colorbar=dict(title="Concluintes"),
            hovertemplate="Região: %{y}<br>%{customdata}<br>Valor: %{z:,.0f}<extra></extra>",
            customdata=np.array(hover_concluintes),
        ),
        row=1,
        col=2,
    )

    fig.update_yaxes(autorange="reversed", row=1, col=1)
    fig.update_yaxes(autorange="reversed", row=1, col=2)
    fig.update_xaxes(tickangle=-18)
    fig.update_layout(height=560, title="Heatmap de acesso ao ensino superior por região e composição demográfica")
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
