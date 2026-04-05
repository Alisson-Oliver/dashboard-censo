import streamlit as st
from src.pages.fluxo_academico.business import FluxoAcademicoService
from src.pages.fluxo_academico import components

# Configuração da página
st.set_page_config(page_title="Fluxo Acadêmico e Evolução")
st.markdown(
    """
    <style>
        .st-emotion-cache-1w723zb {
            max-width: 1200px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Fluxo Acadêmico e Evolução")

# ===== FUNIL E FLUXO POR REGIÃO =====
col1, col2 = st.columns(2)

with col1:
    st.subheader("Funil de Fluxo Acadêmico (2024)")
    with st.spinner("Carregando funil de fluxo..."):
        df_funil = FluxoAcademicoService.get_funil_fluxo_2024()
        fig_funil = components.render_funil_fluxo(df_funil)
        st.plotly_chart(fig_funil, use_container_width=True)

with col2:
    st.subheader("Fluxo por Região (2024)")
    with st.spinner("Carregando fluxo por região..."):
        df_regiao = FluxoAcademicoService.get_fluxo_por_regiao_2024()
        fig_regiao = components.render_fluxo_por_regiao(df_regiao)
        st.plotly_chart(fig_regiao, use_container_width=True)

# ===== DISTRIBUIÇÃO DE TAXAS =====
st.subheader("Distribuição das Taxas de Conclusão por Curso")
with st.spinner("Carregando distribuição das taxas..."):
    df_taxa = FluxoAcademicoService.get_taxa_conclusao_por_curso()
    fig_dist = components.render_distribuicao_taxa_conclusao(df_taxa)
    st.plotly_chart(fig_dist, use_container_width=True)

# ===== ESTATÍSTICAS =====
stats = FluxoAcademicoService.get_estatisticas_taxa_conclusao()
components.render_estatisticas_bloco(stats)

# ===== SCATTER PLOT =====
st.subheader("Taxa de Conclusão vs Total de Matriculados (por curso)")
with st.spinner("Carregando scatter plot..."):
    fig_scatter = components.render_taxa_vs_matriculados(df_taxa)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ===== TOP 10 CURSOS =====
df_menor = FluxoAcademicoService.get_top_cursos_menor_taxa()
df_maior = FluxoAcademicoService.get_top_cursos_maior_taxa()
components.render_top_cursos(df_menor, df_maior)
