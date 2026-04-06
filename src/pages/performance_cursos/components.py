import streamlit as st
import plotly.express as px
import pandas as pd


def render_top_10_cursos(df: pd.DataFrame):
    """Renderiza gráfico de barras do Top 10 Cursos"""
    
    # Montagem do gráfico seguindo o padrão da equipe
    fig = px.bar(
        df,
        x='total_matriculados',
        y='NO_CURSO',
        orientation='h', # Horizontal para caber nomes como "Engenharia de Computação"
        title='Top 10 Cursos com Maiores Matrículas',
        labels={
            'NO_CURSO': 'Curso',
            'total_matriculados': 'Total Matriculado'
        },
        color='total_matriculados',
        color_continuous_scale='Blues',
        text_auto='.2s' # Mantive esse "tempero" para os números ficarem limpos (ex: 1.5M)
    )
    
    # Mantendo a altura padrão do resto do projeto
    fig.update_layout(height=400)
    
    return fig
#############################################################
##--PROGRAMAS DE FINANCIAMENTO---##################
def render_financiamento_comparativo(df: pd.DataFrame):
    """Renderiza gráfico de barras comparativo de financiamentos (FIES vs PROUNI)"""
    
    #Gráfico vertical 
    fig = px.bar(
        df,
        x='Programa',
        y='Total_Matriculas',
        title='Distribuição de Matrículas por Programa de Financiamento',
        labels={
            'Programa': 'Programa Social',
            'Total_Matriculas': 'Total de Alunos'
        },
        color='Total_Matriculas',
        color_continuous_scale='Blues',
        text_auto='.2s' # Mantendo sua formatação limpa (ex: 500k)
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Programas Sociais",
        yaxis_title="Total de Matrículas",
        showlegend=False
    )
    
    return fig