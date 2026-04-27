import streamlit as st
from src.pages.fluxo_academico.business import FluxoAcademicoService
from src.pages.fluxo_academico import components

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

col1, col2 = st.columns(2)

with col2:
    st.subheader("Fluxo por Região (2024)")
    with st.spinner("Carregando fluxo por região..."):
        df_regiao = FluxoAcademicoService.get_fluxo_por_regiao_2024()
        fig_regiao = components.render_fluxo_por_regiao(df_regiao)
        st.plotly_chart(fig_regiao, use_container_width=True)

## Blocos de distribuição e scatter removidos conforme solicitado

df_menor = FluxoAcademicoService.get_top_cursos_menor_taxa()
df_maior = FluxoAcademicoService.get_top_cursos_maior_taxa()
components.render_top_cursos(df_menor, df_maior)
