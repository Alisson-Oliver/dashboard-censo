import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Fluxo Acadêmico e Evolução")

st.title("Fluxo Acadêmico e Evolução")
st.markdown("*Foco: Como os alunos entram, permanecem e saem do sistema?*")


con = duckdb.connect()


st.subheader("Gráfico 1: Evolução Temporal de Ingressantes")
query1 = """
SELECT NU_ANO_CENSO, SUM(QT_ING) as total_ingressantes
FROM read_csv('data.csv', delim=';', encoding='latin-1')
GROUP BY NU_ANO_CENSO
ORDER BY NU_ANO_CENSO
"""
df1 = con.execute(query1).df()
fig1 = px.line(
    df1,
    x="NU_ANO_CENSO",
    y="total_ingressantes",
    title="Evolução de Ingressantes por Ano",
)
st.plotly_chart(fig1)


st.subheader("Gráfico 2: Relação entre Ingressantes e Concluintes por Ano")
query2 = """
SELECT NU_ANO_CENSO, SUM(QT_ING) as total_ingressantes, SUM(QT_CONC) as total_concluintes
FROM read_csv('data.csv', delim=';', encoding='latin-1')
GROUP BY NU_ANO_CENSO
ORDER BY NU_ANO_CENSO
"""
df2 = con.execute(query2).df()
fig2 = go.Figure()
fig2.add_trace(
    go.Bar(x=df2["NU_ANO_CENSO"], y=df2["total_ingressantes"], name="Ingressantes")
)
fig2.add_trace(
    go.Bar(x=df2["NU_ANO_CENSO"], y=df2["total_concluintes"], name="Concluintes")
)
fig2.update_layout(barmode="group", title="Ingressantes vs Concluintes por Ano")
st.plotly_chart(fig2)

# Métricas
st.subheader("Métricas de Cálculo")
query_metricas = """
SELECT 
    SUM(QT_CONC) as total_concluintes,
    SUM(QT_MAT) as total_matriculados,
    (SUM(QT_CONC) / SUM(QT_MAT)) * 100 as taxa_conclusao,
    100 - ((SUM(QT_CONC) / SUM(QT_MAT)) * 100) as evasao_estimada
FROM read_csv('data.csv', delim=';', encoding='latin-1')
"""
df_metricas = con.execute(query_metricas).df()
taxa_conclusao = df_metricas["taxa_conclusao"].iloc[0]
evasao_estimada = df_metricas["evasao_estimada"].iloc[0]
st.metric("Taxa de Conclusão Geral", f"{taxa_conclusao:.2f}%")
st.metric("Evasão Estimada Geral", f"{evasao_estimada:.2f}%")


st.subheader("Gráfico 3: Cursos com Maior Taxa de Evasão")
query3 = """
SELECT NO_CURSO, 
       SUM(QT_CONC) as total_concluintes,
       SUM(QT_MAT) as total_matriculados,
       (SUM(QT_CONC) / SUM(QT_MAT)) * 100 as taxa_conclusao
FROM read_csv('data.csv', delim=';', encoding='latin-1')
GROUP BY NO_CURSO
HAVING SUM(QT_MAT) > 0
ORDER BY taxa_conclusao ASC
LIMIT 10
"""
df3 = con.execute(query3).df()
fig3 = px.bar(
    df3,
    x="NO_CURSO",
    y="taxa_conclusao",
    title="Cursos com Menor Taxa de Conclusão (Maior Evasão)",
    orientation="v",
)
fig3.update_xaxes(tickangle=45)
st.plotly_chart(fig3)

con.close()
