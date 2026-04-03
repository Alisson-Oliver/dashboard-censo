import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Fluxo Acadêmico e Evolução")

st.title("Fluxo Acadêmico e Evolução")


con = duckdb.connect()


st.subheader("Funil de Fluxo Acadêmico (2024)")
query_funil = """
SELECT
    SUM(QT_ING) AS ingressantes,
    SUM(QT_MAT) AS matriculados,
    SUM(QT_CONC) AS concluintes
FROM read_csv('data.csv', delim=';', encoding='latin-1')
WHERE NU_ANO_CENSO = 2024
"""
df_funil = con.execute(query_funil).df().iloc[0]

fig_funil = go.Figure(
    go.Funnel(
        y=["Ingressantes", "Matriculados", "Concluintes"],
        x=[df_funil["ingressantes"], df_funil["matriculados"], df_funil["concluintes"]],
        textinfo="value+percent initial",
    )
)
st.plotly_chart(fig_funil)

# st.write("### Dados usados no funil")
# st.dataframe(
#     pd.DataFrame(
#         {
#             "Etapa": ["Ingressantes", "Matriculados", "Concluintes"],
#             "Contagem": [
#                 df_funil["ingressantes"],
#                 df_funil["matriculados"],
#                 df_funil["concluintes"],
#             ],
#         }
#     )
# )

st.subheader("Fluxo por Região (2024)")
query_regiao = """
SELECT NO_REGIAO,
       SUM(QT_ING) AS ingressantes,
       SUM(QT_MAT) AS matriculados,
       SUM(QT_CONC) AS concluintes
FROM read_csv('data.csv', delim=';', encoding='latin-1')
WHERE NU_ANO_CENSO = 2024
GROUP BY NO_REGIAO
ORDER BY NO_REGIAO
"""
df_regiao = con.execute(query_regiao).df()

fig2 = go.Figure()
fig2.add_trace(
    go.Bar(x=df_regiao["NO_REGIAO"], y=df_regiao["ingressantes"], name="Ingressantes")
)
fig2.add_trace(
    go.Bar(x=df_regiao["NO_REGIAO"], y=df_regiao["matriculados"], name="Matriculados")
)
fig2.add_trace(
    go.Bar(x=df_regiao["NO_REGIAO"], y=df_regiao["concluintes"], name="Concluintes")
)
fig2.update_layout(
    barmode="group",
    title="Fluxo Acadêmico por Região (2024)",
    xaxis_title="Região",
    yaxis_title="Quantidade",
)
st.plotly_chart(fig2)

# st.write("### Tabela de fluxo por região")
# st.dataframe(df_regiao)


st.subheader("Relação entre Ingressantes e Concluintes em 2024")
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


st.subheader("Distribuição das Taxas de Conclusão por Curso")
query3_all = """
SELECT NO_CURSO,
       SUM(QT_CONC) AS total_concluintes,
       SUM(QT_MAT) AS total_matriculados,
       (SUM(QT_CONC) / SUM(QT_MAT)) * 100 AS taxa_conclusao
FROM read_csv('data.csv', delim=';', encoding='latin-1')
GROUP BY NO_CURSO
HAVING SUM(QT_MAT) > 0
"""
df3_all = con.execute(query3_all).df()


fig_dist = px.histogram(
    df3_all,
    x="taxa_conclusao",
    nbins=20,
    title="Distribuição das Taxas de Conclusão (todos os cursos)",
    labels={"taxa_conclusao": "Taxa de Conclusão (%)", "count": "Número de Cursos"},
    color_discrete_sequence=["lightblue"],
)
fig_dist.update_layout(
    xaxis_title="Taxa de Conclusão (%)",
    yaxis_title="Número de Cursos",
    bargap=0.1,
)
st.plotly_chart(fig_dist)

# Adicionar estatísticas
st.write("### Estatísticas das Taxas de Conclusão")
st.write(f"- Média: {df3_all['taxa_conclusao'].mean():.2f}%")
st.write(f"- Mediana: {df3_all['taxa_conclusao'].median():.2f}%")
st.write(f"- Mínimo: {df3_all['taxa_conclusao'].min():.2f}%")
st.write(f"- Máximo: {df3_all['taxa_conclusao'].max():.2f}%")
st.write(f"- Cursos com 0%: {(df3_all['taxa_conclusao'] == 0).sum()}")
st.write(f"- Cursos com 100%: {(df3_all['taxa_conclusao'] == 100).sum()}")
# Normalização e análise adicional
st.subheader("Gráfico 4: Taxa de Conclusão vs Total de Matriculados (por curso)")
fig4 = px.scatter(
    df3_all,
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
fig4.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color="DarkSlateGrey")))
fig4.update_layout(
    xaxis_type="log",
    xaxis_title="Total Matriculados (escala log)",
    yaxis_title="Taxa de Conclusão (%)",
    legend_title="Taxa de Conclusão",
)
st.plotly_chart(fig4)

min_matriculados = 40
filtered = df3_all[df3_all["total_matriculados"] >= min_matriculados]

# Manter os top 10, mas em formato de tabela ou scatter
df3_low = df3_all.sort_values("taxa_conclusao", ascending=True).head(10)
df3_high = df3_all.sort_values("taxa_conclusao", ascending=False).head(10)

st.subheader("Top 10 Cursos com Menor Taxa de Conclusão")
st.dataframe(df3_low[["NO_CURSO", "total_matriculados", "taxa_conclusao"]])

st.subheader("Top 10 Cursos com Maior Taxa de Conclusão")
st.dataframe(df3_high[["NO_CURSO", "total_matriculados", "taxa_conclusao"]])



con.close()
