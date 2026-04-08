import os
import sys

import streamlit as st


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def main():
    try:
        from src.pages.performance_cursos.business import PerformanceService
        from src.pages.performance_cursos.components import (
            render_financiamento_comparativo,
            render_ingresso_comparativo,
            render_taxa_conclusao,
            render_top_10_cursos,
        )
    except ModuleNotFoundError as e:
        st.error(f"Erro ao localizar os módulos do projeto: {e}")
        st.info(f"Caminho tentado: {root_dir}")
        return

    st.set_page_config(page_title="Performance de Cursos", layout="wide")
    st.title("Performance de Cursos e Indicadores Sociais")
    st.divider()

    try:
        with st.spinner("Carregando dados..."):
            df_top_10 = PerformanceService.get_top_10_curso()
            df_fin = PerformanceService.get_financiamento_comparativo()
            df_ing = PerformanceService.get_ingresso_comparativo()
            df_tree = PerformanceService.get_conclusao_hierarquia()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 Cursos com Maiores Matrículas")
            fig_top_10 = render_top_10_cursos(df_top_10)
            st.plotly_chart(fig_top_10, use_container_width=True)

        with col2:
            st.subheader("Participação em Programas de Financiamento")
            fig_fin = render_financiamento_comparativo(df_fin)
            st.plotly_chart(fig_fin, use_container_width=True)

        st.divider()

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Formas de Ingresso: ENEM vs VESTIBULAR")
            fig_ing = render_ingresso_comparativo(df_ing)
            st.plotly_chart(fig_ing, use_container_width=True)

        with col4:
            st.subheader("Taxa de Conclusão por Região e Curso")
            fig_tree = render_taxa_conclusao(df_tree)
            st.plotly_chart(fig_tree, use_container_width=True)

    except Exception as e:
        st.error("Erro na execução do dashboard.")
        st.exception(e)


if __name__ == "__main__":
    main()