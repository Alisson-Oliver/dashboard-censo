import sys
import os
import streamlit as st

#CONFIGURAÇÃO DE CAMINHO
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir) #prioridade máxima a esse caminho

def main():
    #IMPORTAÇÃO ATRASADA (Lazy Import)
    try:
        from src.pages.performance_cursos.business import PerformanceService
        from src.pages.performance_cursos.components import render_top_10_cursos
        from src.pages.performance_cursos.components import render_financiamento_comparativo
        from src.pages.performance_cursos.components import render_ingresso_comparativo 
    except ModuleNotFoundError as e:
        st.error(f"Erro ao localizar os módulos do projeto: {e}")
        st.info(f"Caminho tentado: {root_dir}")
        return

    #######################################################################
    ##--------------------TOP 10 CURSO COM MAIORES MATRICULAS--------------
    st.set_page_config(page_title="Performance de Cursos", layout="wide")
    st.title("Performance de Cursos e Indicadores Sociais")
    st.divider()

    try:
        with st.spinner("Carregando dados..."):
            df_top_10 = PerformanceService.get_top_10_curso()
            fig = render_top_10_cursos(df_top_10)
            st.plotly_chart(fig, use_container_width=True)
    ############################################################
    # ---PROGRAMAS DE FINANCIAMENTO ---
            # Usando colunas para dar um destaque diferente se quiser, 
            # ou mantendo largura total como o anterior:
            st.subheader("Participação em Programas de Financiamento")
            
            df_fin = PerformanceService.get_financiamento_comparativo()
            fig_fin = render_financiamento_comparativo(df_fin)
            st.plotly_chart(fig_fin, use_container_width=True)        
 #####################################################################
                         #---Forma de Ingresso-----
            st.divider()
            st.subheader("Formas de Ingresso: ENEM vs VESTIBULAR")
            df_ing = PerformanceService.get_ingresso_comparativo()
            fig_ing = render_ingresso_comparativo(df_ing)
            st.plotly_chart(fig_ing, use_container_width=True)

           
    
    except Exception as e:
        st.error("Erro na execução do dashboard.")
        st.exception(e) #Isso mostra o erro detalhado para a gente depurar



if __name__ == "__main__":
    main()