import streamlit as st
from src.pages.visao_geral.business import VisaoGeralService
from src.pages.visao_geral import components

# Configuração da página
st.set_page_config(page_title="Visão Geral e Distribuição Geográfica")

st.title("Visão Geral e Distribuição Geográfica")
st.markdown("Onde estão os alunos e as instituições?")

anos_disponiveis = VisaoGeralService.get_anos_disponiveis()
ano_selecionado = anos_disponiveis[0]

# ===== SEÇÃO 1: DISTRIBUIÇÃO POR REGIÃO =====
st.header("Distribuição Regional")

col1, col2 = st.columns(2)

with col1:
    with st.spinner("Carregando dados por região..."):
        df_regiao = VisaoGeralService.get_matriculas_por_regiao(ano_selecionado)
        st.subheader("Alunos por Região")
        fig_regiao = components.render_matriculas_por_regiao(df_regiao)
        st.plotly_chart(fig_regiao, use_container_width=True)

with col2:
    with st.spinner("Carregando instituições..."):
        df_instituicoes = VisaoGeralService.get_instituicoes_por_regiao(ano_selecionado)
        st.subheader("Instituições por Região")
        fig_instituicoes = components.render_instituicoes_por_regiao(df_instituicoes)
        st.plotly_chart(fig_instituicoes, use_container_width=True)

# ===== SEÇÃO 2: MAPA GEOGRÁFICO =====
with st.spinner("Carregando estados..."):
    df_estados = VisaoGeralService.get_matriculas_por_estado(ano_selecionado)
    st.header("Top 15 Estados")
    fig_mapa = components.render_mapa_matriculas_por_estado(df_estados)
    st.plotly_chart(fig_mapa, use_container_width=True)

# ===== SEÇÃO 3: CATEGORIA E MODALIDADE =====
st.header("Análise por Tipo de Instituição e Modalidade")
with st.spinner("Carregando análise comparativa..."):
    df_categoria = VisaoGeralService.get_matriculas_por_categoria(ano_selecionado)
    df_modalidade = VisaoGeralService.get_matriculas_por_modalidade(ano_selecionado)
    components.render_matriz_categoria_modalidade(df_categoria, df_modalidade)

# ===== TABELA RESUMIDA =====
st.header("Resumo por Região")
with st.spinner("Carregando resumo..."):
    df_resumo = VisaoGeralService.get_matriculas_por_regiao(ano_selecionado)
    df_resumo = df_resumo.dropna()
    st.dataframe(df_resumo, use_container_width=True)
