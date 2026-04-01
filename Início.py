import streamlit as st

st.set_page_config(
    page_title="Censo Curso Superior 2024 | Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .hero {
            padding: 2.2rem 2rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #38bdf8 100%);
            color: white;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.20);
            margin-bottom: 1.5rem;
        }
        .hero h1 {
            font-size: 2.4rem;
            margin-bottom: 0.4rem;
            line-height: 1.1;
        }
        .hero p {
            font-size: 1.05rem;
            max-width: 820px;
            opacity: 0.95;
            margin-bottom: 0;
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin: 1.4rem 0 0.6rem;
        }
        .card {
            padding: 1.2rem 1.1rem;
            border-radius: 18px;
            border: 1px solid rgba(15, 23, 42, 0.10);
            background: white;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.05);
            min-height: 190px;
        }
        .card h3 {
            margin-top: 0;
            margin-bottom: 0.5rem;
        }
        .card p {
            margin-bottom: 0.9rem;
            color: #475569;
        }
        .tag {
            display: inline-block;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            background: #e0f2fe;
            color: #075985;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
        }
        .hint {
            padding: 1rem 1.1rem;
            border-radius: 16px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            color: #334155;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Censo Curso Superior 2024</h1>
        <p>
            Painel para explorar distribuição geográfica, fluxo acadêmico, perfil socioeconômico
            e desempenho dos cursos em uma navegação rápida e organizada.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# col1, col2, col3 = st.columns(3)
# col1.metric("Áreas de análise", "4")
# col2.metric("Navegação", "Menu lateral")
# col3.metric("Base do projeto", "Streamlit")

st.markdown('<div class="section-title">Acesso rápido</div>', unsafe_allow_html=True)

pages = [
    {
        "title": "Visão Geral e Distribuição Geográfica",
        "description": "Veja o panorama do país e a distribuição das instituições por região.",
        "icon": "🌎",
        "path": "pages/1_Visão_Geral_e_Distribuição_Geográfica.py",
        "tag": "Mapa e panorama",
    },
    {
        "title": "Fluxo Acadêmico e Evolução",
        "description": "Analise trajetórias, movimentações e evolução dos estudantes ao longo do tempo.",
        "icon": "📈",
        "path": "pages/2_Fluxo_Acadêmico_e_Evolução.py",
        "tag": "Trajetória acadêmica",
    },
    {
        "title": "Perfil Socioeconômico do Estudante",
        "description": "Explore características sociais e econômicas do público atendido pelo ensino superior.",
        "icon": "👥",
        "path": "pages/3_Perfil_Socioeconômico_do_Estudante.py",
        "tag": "Perfil estudantil",
    },
    {
        "title": "Performance de Cursos e eSocial",
        "description": "Acompanhe indicadores de curso e informações relacionadas ao eSocial.",
        "icon": "⭐",
        "path": "pages/4_Performance de Cursos e_Social.py",
        "tag": "Desempenho",
    },
]

cols = st.columns(2)
page_link = getattr(st, "page_link", None)

for index, page in enumerate(pages):
    with cols[index % 2]:
        st.markdown(
            f'''
            <div class="card">
                <div class="tag">{page["tag"]}</div>
                <h3>{page["icon"]} {page["title"]}</h3>
                <p>{page["description"]}</p>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        if callable(page_link):
            page_link(page["path"], label=f"Abrir {page['title']}", icon="➡️")
        else:
            st.markdown(f"[Abrir {page['title']}]({page['path']})")

# st.markdown('<div class="section-title">Como navegar</div>', unsafe_allow_html=True)
# st.markdown(
#     """
#     <div class="hint">
#         Use o menu lateral para alternar entre as páginas analíticas. Esta home funciona como ponto de entrada
#         e atalho para os temas principais do dashboard.
#     </div>
#     """,
#     unsafe_allow_html=True,
# )
