import streamlit as st

from src.database import get_db

st.set_page_config(
    page_title="Censo Curso Superior 2024 | Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def get_kpis() -> dict:
    db = get_db()
    data_path = db.get_data_path()

    query = f"""
    SELECT
        MAX(NU_ANO_CENSO) AS ano_referencia,
        SUM(QT_MAT) AS total_matriculas,
        SUM(QT_ING) AS total_ingressantes,
        SUM(QT_CONC) AS total_concluintes,
        COUNT(DISTINCT CO_IES) AS total_ies,
        COUNT(DISTINCT CO_CURSO) AS total_cursos,
        SUM(CASE WHEN TP_MODALIDADE_ENSINO = 2 THEN QT_MAT ELSE 0 END) AS total_matriculas_ead
    FROM read_csv('{data_path}', delim=';', encoding='latin-1')
    """

    df = db.execute_query(query).df()
    row = df.iloc[0]

    total_matriculas = float(row["total_matriculas"] or 0)
    total_concluintes = float(row["total_concluintes"] or 0)
    total_ead = float(row["total_matriculas_ead"] or 0)

    return {
        "ano_referencia": int(row["ano_referencia"] or 0),
        "total_matriculas": int(total_matriculas),
        "total_ingressantes": int(row["total_ingressantes"] or 0),
        "total_concluintes": int(total_concluintes),
        "total_ies": int(row["total_ies"] or 0),
        "total_cursos": int(row["total_cursos"] or 0),
        "taxa_conclusao": (total_concluintes / total_matriculas * 100) if total_matriculas else 0,
        "participacao_ead": (total_ead / total_matriculas * 100) if total_matriculas else 0,
    }

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Manrope:wght@400;600;700&display=swap');

        :root,
        [data-theme="light"] {
            --surface-card: #ffffff;
            --surface-soft: #f8fafc;
            --border-soft: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #475569;
            --tag-bg: #e0f2fe;
            --tag-text: #075985;
            --kpi-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
            --card-shadow: 0 10px 25px rgba(15, 23, 42, 0.05);
        }

        [data-theme="dark"],
        html[data-theme="dark"],
        body[data-theme="dark"] {
            --surface-card: linear-gradient(180deg, rgba(17, 24, 39, 0.92) 0%, rgba(15, 23, 42, 0.95) 100%);
            --surface-soft: rgba(15, 23, 42, 0.72);
            --border-soft: rgba(148, 163, 184, 0.28);
            --text-main: #f1f5f9;
            --text-muted: #cbd5e1;
            --tag-bg: rgba(30, 58, 95, 0.78);
            --tag-text: #bae6fd;
            --kpi-shadow: 0 12px 28px rgba(2, 6, 23, 0.45);
            --card-shadow: 0 12px 30px rgba(2, 6, 23, 0.40);
        }

        html, body, [class*="css"]  {
            font-family: 'Manrope', sans-serif;
        }
        .hero {
            padding: 2.4rem 2.2rem;
            border-radius: 24px;
            background:
                radial-gradient(circle at 84% 18%, rgba(253, 186, 116, 0.28) 0%, rgba(253, 186, 116, 0) 35%),
                linear-gradient(128deg, #0a1e45 0%, #0b3a7e 46%, #0ea5e9 100%);
            color: white;
            box-shadow: 0 18px 45px rgba(8, 25, 57, 0.22);
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        .hero h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.35rem;
            margin-bottom: 0.4rem;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }
        .hero p {
            font-size: 1.05rem;
            max-width: 820px;
            opacity: 0.95;
            margin-bottom: 0;
        }
        .kpi-card {
            padding: 1.05rem 1rem;
            border-radius: 16px;
            border: 1px solid var(--border-soft);
            background: var(--surface-card);
            box-shadow: var(--kpi-shadow);
            min-height: 118px;
        }
        .kpi-label {
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.3rem;
        }
        .kpi-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.65rem;
            font-weight: 700;
            color: var(--text-main);
            margin: 0;
            line-height: 1.1;
        }
        .kpi-sub {
            margin-top: 0.35rem;
            font-size: 0.86rem;
            color: var(--text-muted);
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin: 1.4rem 0 0.6rem;
            color: var(--text-main);
        }
        .card {
            padding: 1.2rem 1.1rem;
            border-radius: 18px;
            border: 1px solid var(--border-soft);
            background: var(--surface-card);
            box-shadow: var(--card-shadow);
            min-height: 190px;
        }
        .card h3 {
            margin-top: 0;
            margin-bottom: 0.5rem;
            color: var(--text-main);
        }
        .card p {
            margin-bottom: 0.9rem;
            color: var(--text-muted);
        }
        .tag {
            display: inline-block;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            background: var(--tag-bg);
            color: var(--tag-text);
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
        }
        .hint {
            padding: 1rem 1.1rem;
            border-radius: 16px;
            background: var(--surface-soft);
            border: 1px solid var(--border-soft);
            color: var(--text-muted);
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

kpis = get_kpis()

kpi_cols = st.columns(4)

metric_cards = [
    ("Matrículas Totais", f"{kpis['total_matriculas']:,}".replace(",", "."), "Volume total de estudantes no ensino superior"),
    ("Ingressantes", f"{kpis['total_ingressantes']:,}".replace(",", "."), "Entrada acumulada no período disponível"),
    ("Concluintes", f"{kpis['total_concluintes']:,}".replace(",", "."), f"Taxa geral de conclusão: {kpis['taxa_conclusao']:.1f}%"),
    ("Total de Cursos Cadastrados", f"{kpis['total_cursos']:,}".replace(",", "."), "Quantidade de cursos únicos cadastrados"),
]

for i, (label, value, sub) in enumerate(metric_cards):
    with kpi_cols[i]:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <p class="kpi-value">{value}</p>
                <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div class="section-title">Acesso rápido</div>', unsafe_allow_html=True)

pages = [
    {
        "title": "Visão Geral e Distribuição Geográfica",
        "description": "Veja o panorama do país e a distribuição das instituições por região.",
        "icon": "",
        "path": "pages/1_Visão_Geral_e_Distribuição_Geográfica.py",
        "tag": "Mapa e panorama",
    },
    {
        "title": "Fluxo Acadêmico e Evolução",
        "description": "Analise trajetórias, movimentações e evolução dos estudantes ao longo do tempo.",
        "icon": "",
        "path": "pages/2_Fluxo_Acadêmico_e_Evolução.py",
        "tag": "Trajetória acadêmica",
    },
    {
        "title": "Perfil Socioeconômico do Estudante",
        "description": "Explore características sociais e econômicas do público atendido pelo ensino superior.",
        "icon": "",
        "path": "pages/3_Perfil_Socioeconômico_do_Estudante.py",
        "tag": "Perfil estudantil",
    },
    {
        "title": "Performance de Cursos e eSocial",
        "description": "Acompanhe indicadores de curso e informações relacionadas ao cenário social.",
        "icon": "",
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
