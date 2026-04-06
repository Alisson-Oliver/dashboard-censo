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