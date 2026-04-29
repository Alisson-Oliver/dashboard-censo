import os
import sys

import streamlit as st


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

st.set_page_config(page_title="Perfil Socioeconômico do Estudante", layout="wide")


def main():
    try:
        from src.pages.perfil_socioeconomico.business import PerfilSocioeconomicoService
        from src.pages.perfil_socioeconomico.components import (
            render_bar_horizontal,
            render_duas_metricas,
            render_pie_chart,
        )
    except ModuleNotFoundError as e:
        st.error(f"Erro ao localizar os módulos do projeto: {e}")
        st.info(f"Caminho tentado: {root_dir}")
        return

    st.title("Perfil Socioeconômico do Estudante")
    st.markdown("Composição social, demográfica e de apoio estudantil no Censo da Educação Superior.")

    with st.spinner("Carregando distribuição por sexo e faixa etária..."):
        df_genero = PerfilSocioeconomicoService.get_distribuicao_genero()
        df_idade = PerfilSocioeconomicoService.get_faixa_etaria()

    st.header("Identidade e Faixa Etária")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribuição por Sexo")
        fig_genero = render_pie_chart(df_genero, "Distribuição de Matrículas por Sexo")
        st.plotly_chart(fig_genero, use_container_width=True)

    with col2:
        st.subheader("Distribuição por Idade")
        fig_idade = render_bar_horizontal(df_idade, "Distribuição de Matrículas por Faixa Etária")
        st.plotly_chart(fig_idade, use_container_width=True)

    with st.spinner("Carregando perfil racial e deficiência..."):
        df_raca = PerfilSocioeconomicoService.get_raca_cor()
        df_deficiencia = PerfilSocioeconomicoService.get_deficiencia()

    st.header("Raça/Cor e Inclusão")
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Distribuição por Raça/Cor")
        fig_raca = render_bar_horizontal(df_raca, "Distribuição de Matrículas por Raça/Cor")
        st.plotly_chart(fig_raca, use_container_width=True)

    with col4:
        st.subheader("Estudantes com Deficiência")
        fig_deficiencia = render_pie_chart(df_deficiencia, "Estudantes com e sem Deficiência")
        st.plotly_chart(fig_deficiencia, use_container_width=True)

    with st.spinner("Carregando financiamento e reserva de vaga..."):
        df_financiamento = PerfilSocioeconomicoService.get_financiamento()
        df_reserva_vaga = PerfilSocioeconomicoService.get_reserva_vaga()

    st.header("Acesso e Permanência")
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Programas de Financiamento")
        fig_financiamento = render_pie_chart(df_financiamento, "Participação em Programas de Financiamento")
        st.plotly_chart(fig_financiamento, use_container_width=True)

    with col6:
        st.subheader("Reserva de Vagas")
        fig_reserva_vaga = render_bar_horizontal(df_reserva_vaga, "Uso de Reserva de Vagas")
        st.plotly_chart(fig_reserva_vaga, use_container_width=True)

    with st.spinner("Carregando apoio social e mobilidade..."):
        df_apoio_social = PerfilSocioeconomicoService.get_apoio_social_individual()
        df_atividades = PerfilSocioeconomicoService.get_atividades_extracurriculares_individual()
        df_mobilidade = PerfilSocioeconomicoService.get_mobilidade_academica_individual()

    st.header("Apoio Social e Vida Acadêmica")
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Apoio Social")
        fig_apoio_social = render_pie_chart(df_apoio_social, "Apoio Social")
        st.plotly_chart(fig_apoio_social, use_container_width=True)

    with col6:
        st.subheader("Atividades Extracurriculares")
        fig_atividades = render_pie_chart(df_atividades, "Atividades Extracurriculares")
        st.plotly_chart(fig_atividades, use_container_width=True)





















if __name__ == "__main__":
    main()