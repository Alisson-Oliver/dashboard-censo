import plotly.express as px
import pandas as pd


def render_pie_chart(df: pd.DataFrame, title: str):
    """Renderiza um gráfico de rosca para distribuição percentual."""

    fig = px.pie(
        df,
        names="categoria",
        values="total",
        title=title,
        hole=0.45,
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig.update_traces(
        textinfo="label+percent",
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>Total: %{value:.0f}<br>Participação: %{percent}",
        marker=dict(line=dict(color="#FFFFFF", width=2)),
    )
    fig.update_layout(height=420, margin=dict(t=60, b=30, l=20, r=20), showlegend=False)
    return fig


def render_bar_horizontal(df: pd.DataFrame, title: str):
    """Renderiza um gráfico de barras horizontal ordenado."""

    df_sorted = df.sort_values("total", ascending=True)
    fig = px.bar(
        df_sorted,
        x="total",
        y="categoria",
        orientation="h",
        title=title,
        labels={"categoria": "Categoria", "total": "Total"},
        color="total",
        color_continuous_scale="Blues",
        text_auto=".2s",
    )
    fig.update_layout(height=max(420, 35 * len(df_sorted) + 120), showlegend=False, margin=dict(t=60, b=20, l=20, r=20))
    return fig


def render_duas_metricas(df: pd.DataFrame, title: str):
    """Renderiza um gráfico de barras para indicadores sociais e acadêmicos."""

    fig = px.bar(
        df,
        x="categoria",
        y="total",
        title=title,
        labels={"categoria": "Indicador", "total": "Total"},
        color="total",
        color_continuous_scale="Blues",
        text_auto=".2s",
    )
    fig.update_layout(height=420, xaxis_tickangle=-20, showlegend=False, margin=dict(t=60, b=40, l=20, r=20))
    return fig
