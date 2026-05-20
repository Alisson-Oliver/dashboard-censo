import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render_funil_fluxo(df_funil: pd.Series):
    """Renderiza o funil de fluxo acadêmico"""
    fig = go.Figure(
        data=[
            go.Funnel(
                y=["Calouros", "Veteranos", "Concluintes"],
                x=[
                    df_funil["ingressantes"],
                    df_funil["matriculados"],
                    df_funil["concluintes"],
                ],
                textinfo="value+percent initial",
                marker=dict(color=["#2563eb", "#0ea5e9", "#ef4444"]),
            )
        ]
    )
    return fig


def render_fluxo_por_regiao(df_regiao: pd.DataFrame):
    """Renderiza o gráfico de fluxo por região"""
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_regiao["NO_REGIAO"],
            y=df_regiao["ingressantes"],
            name="Calouros",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_regiao["NO_REGIAO"],
            y=df_regiao["matriculados"],
            name="Veteranos",
        )
    )
    fig.add_trace(
        go.Bar(x=df_regiao["NO_REGIAO"], y=df_regiao["concluintes"], name="Concluintes")
    )

    fig.update_layout(
        barmode="group",
        title="Fluxo Acadêmico por Região (2024)",
        xaxis_title="Região",
        yaxis_title="Quantidade",
    )

    return fig


def render_distribuicao_taxa_conclusao(df: pd.DataFrame):
    """Renderiza histograma de distribuição de taxas de conclusão"""
    fig = px.histogram(
        df,
        x="taxa_conclusao",
        nbins=20,
        title="Distribuição das Taxas de Conclusão (todos os cursos)",
        labels={"taxa_conclusao": "Taxa de Conclusão (%)", "count": "Número de Cursos"},
        color_discrete_sequence=["lightblue"],
    )

    fig.update_layout(
        xaxis_title="Taxa de Conclusão (%)",
        yaxis_title="Número de Cursos",
        bargap=0.1,
    )

    return fig


def render_taxa_vs_matriculados(df: pd.DataFrame):
    """Renderiza scatter plot de taxa de conclusão vs matriculados"""
    fig = px.scatter(
        df,
        x="total_matriculados",
        y="taxa_conclusao",
        size="total_matriculados",
        color="taxa_conclusao",
        hover_name="NO_CURSO",
        title="Taxa de Conclusão vs Tamanho do Curso",
        labels={
            "total_matriculados": "Total Matriculados",
            "taxa_conclusao": "Taxa de Conclusão (%)",
        },
        size_max=80,
    )

    fig.update_traces(
        marker=dict(opacity=0.8, line=dict(width=1, color="DarkSlateGrey"))
    )
    fig.update_layout(
        xaxis_type="log",
        xaxis_title="Total Matriculados (escala log)",
        yaxis_title="Taxa de Conclusão (%)",
        legend_title="Taxa de Conclusão",
    )

    return fig


def render_estatisticas_bloco(stats: dict):
    """Renderiza bloco de estatísticas"""
    st.write("### Estatísticas das Taxas de Conclusão")
    st.write(f"- Média: {stats['media']:.2f}%")
    st.write(f"- Mediana: {stats['mediana']:.2f}%")
    st.write(f"- Mínimo: {stats['minimo']:.2f}%")
    st.write(f"- Máximo: {stats['maximo']:.2f}%")
    st.write(f"- Cursos com 0%: {stats['cursos_0_pct']}")
    st.write(f"- Cursos com 100%: {stats['cursos_100_pct']}")


def render_top_cursos(df_menor: pd.DataFrame, df_maior: pd.DataFrame):
    """Renderiza tabelas de top cursos"""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Cursos com Menor Taxa de Conclusão")
        st.dataframe(
            df_menor[["NO_CURSO", "total_matriculados", "taxa_conclusao"]],
            use_container_width=True,
        )

    with col2:
        st.subheader("Top 10 Cursos com Maior Taxa de Conclusão")
        st.dataframe(
            df_maior[["NO_CURSO", "total_matriculados", "taxa_conclusao"]],
            use_container_width=True,
        )
