import sys
import os
import streamlit as st

# 1. CONFIGURAÇÃO DE CAMINHO (Obrigatório ser o primeiro bloco)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir) # O '0' dá prioridade máxima a esse caminho

def main():
    # 2. IMPORTAÇÃO ATRASADA (Lazy Import)
    # Importamos aqui dentro para garantir que o sys.path já foi alterado
    try:
        from src.pages.performance_cursos.business import PerformanceService
        from src.pages.performance_cursos.components import render_top_10_cursos
    except ModuleNotFoundError as e:
        st.error(f"Erro ao localizar os módulos do projeto: {e}")
        st.info(f"Caminho tentado: {root_dir}")
        return

    # 3. INTERFACE
    st.set_page_config(page_title="Performance de Cursos", layout="wide")
    st.title("Performance de Cursos e Indicadores Sociais")
    st.divider()

    try:
        with st.spinner("Carregando dados..."):
            df_top_10 = PerformanceService.get_top_10_curso()
            fig = render_top_10_cursos(df_top_10)
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error("Erro na execução do dashboard.")
        st.exception(e) # Isso mostra o erro detalhado para a gente depurar

if __name__ == "__main__":
    main()