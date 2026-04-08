import streamlit as st
import plotly.express as px
import pandas as pd


def render_top_10_cursos(df: pd.DataFrame):
    """Renderiza gráfico de barras do Top 10 Cursos"""
    fig = px.bar(
        df,
        x='total_matriculados',
        y='NO_CURSO',
        orientation='h',
        title='Top 10 Cursos com Maiores Matrículas',
        labels={
            'NO_CURSO': 'Curso',
            'total_matriculados': 'Total Matriculado'
        },
        color='total_matriculados',
        color_continuous_scale='Blues',
        text_auto='.2s'
    )
    
    fig.update_layout(height=400)
    
    return fig

def render_financiamento_comparativo(df: pd.DataFrame):
    """Renderiza gráfico de barras comparativo de financiamentos (FIES vs PROUNI)"""
    
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
        text_auto='.2s'
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Programas Sociais",
        yaxis_title="Total de Matrículas",
        showlegend=False
    )
    
    return fig

def render_ingresso_comparativo(df: pd.DataFrame):
    """Renderiza gráfico de pizza com números totais sempre visíveis"""
    
    fig = px.pie(
        df, 
        values='Total_Ingressantes', 
        names='Forma_Ingresso', 
        title='Proporção de Ingresso: ENEM vs VESTIBULAR',
        color_discrete_sequence=px.colors.sequential.Blues_r,
        labels={'Forma_Ingresso': 'Tipo', 'Total_Ingressantes': 'Total'}
    )
    
    fig.update_traces(
        textinfo='label+value',
        texttemplate='%{label}: %{value:.2s}',
        textposition='outside',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    fig.update_layout(
        height=450, 
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def render_taxa_conclusao(df: pd.DataFrame):
    fig = px.treemap(
        df,
        path=[px.Constant("Brasil"), 'Regiao', 'Curso'],
        values='Taxa_Conclusao',
        color='Taxa_Conclusao',
        color_continuous_scale='Blues',
        title='Relacionamento: Região x Curso (Tamanho por Taxa de Conclusão)',
        labels={'Taxa_Conclusao': 'Taxa de Conclusão (%)'}
    )
    
    fig.update_traces(
        textinfo="label+value",
        texttemplate='%{label}<br>%{value:.2f}%',
        hovertemplate='<b>%{label}</b><br>Região: %{parent}<br>Taxa: %{value:.2f}%'
    )
    
    fig.update_layout(
        height=650,
        margin=dict(t=50, l=10, r=10, b=10)
    )
    
    return fig 
