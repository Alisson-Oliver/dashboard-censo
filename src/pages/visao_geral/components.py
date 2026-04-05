import streamlit as st
import plotly.express as px
import pandas as pd


def render_matriculas_por_regiao(df: pd.DataFrame):
    """Renderiza gráfico de distribuição de matrículas por região"""
    fig = px.bar(
        df,
        x='NO_REGIAO',
        y='total_matriculados',
        title='Distribuição de Alunos Matriculados por Região',
        labels={
            'NO_REGIAO': 'Região',
            'total_matriculados': 'Total Matriculado'
        },
        color='total_matriculados',
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=400)
    return fig


def render_mapa_matriculas_por_estado(df: pd.DataFrame):
    """Renderiza gráfico de matrículas por estado"""
    df_sorted = df.sort_values('total_matriculados', ascending=True).tail(15)
    
    fig = px.bar(
        df_sorted,
        x='total_matriculados',
        y='NO_UF',
        orientation='h',
        title='Top 15 Estados (Concentração de Estudantes)',
        labels={
            'total_matriculados': 'Total Matriculado',
            'NO_UF': 'Estado'
        },
        color='total_matriculados',
        color_continuous_scale='YlGnBu'
    )
    fig.update_layout(height=500, showlegend=False)
    return fig


def render_instituicoes_por_regiao(df: pd.DataFrame):
    """Renderiza gráfico de quantidade de instituições por região"""
    fig = px.bar(
        df,
        x='NO_REGIAO',
        y='quantidade_instituicoes',
        title='Quantidade de Instituições de Ensino por Região',
        labels={
            'NO_REGIAO': 'Região',
            'quantidade_instituicoes': 'Quantidade de Instituições'
        },
        color='quantidade_instituicoes',
        color_continuous_scale='Greens'
    )
    fig.update_layout(height=400)
    return fig


def render_matriz_categoria_modalidade(df_categoria: pd.DataFrame, df_modalidade: pd.DataFrame):
    """Renderiza comparativo de categoria e modalidade lado a lado"""
    col1, col2 = st.columns(2)
    
    with col1:
        fig_cat = px.pie(
            df_categoria,
            names='categoria',
            values='total_matriculados',
            title='Distribuição: Instituições Públicas vs Privadas',
            hole=0.3
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        fig_mod = px.pie(
            df_modalidade,
            names='TP_MODALIDADE_ENSINO',
            values='total_matriculados',
            title='Distribuição: Presencial vs EAD',
            hole=0.3
        )
        st.plotly_chart(fig_mod, use_container_width=True)
