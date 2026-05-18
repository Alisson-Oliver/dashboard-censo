from __future__ import annotations

import os
import sys

import streamlit as st


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

st.set_page_config(page_title="INEP + Etnia | Dashboard Analítico", layout="wide")


def _format_number(value: float | int) -> str:
    return f"{int(value):,}".replace(",", ".")


def _render_kpi(label: str, value: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div style="padding:1rem 1.1rem;border-radius:18px;border:1px solid rgba(148,163,184,0.25);background:linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);box-shadow:0 10px 25px rgba(15,23,42,0.06);min-height:110px;">
            <div style="font-size:0.78rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#475569;margin-bottom:0.35rem;">{label}</div>
            <div style="font-size:1.75rem;font-weight:800;color:#0f172a;line-height:1.1;">{value}</div>
            <div style="margin-top:0.35rem;font-size:0.86rem;color:#475569;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    try:
        from src.pages.integrada_inep_etnia.business import create_charts, create_kpis, load_data, transform_data
    except ModuleNotFoundError as exc:
        st.error(f"Erro ao localizar os módulos do projeto: {exc}")
        st.info(f"Caminho tentado: {root_dir}")
        return

    st.markdown(
        """
        <style>
            html, body, [class*="css"] {
                font-family: Inter, system-ui, sans-serif;
            }
            .hero-wrap {
                padding: 2rem 2rem 1.8rem;
                border-radius: 26px;
                background: linear-gradient(125deg, #081122 0%, #0f3a63 50%, #0f766e 100%);
                color: white;
                border: 1px solid rgba(255,255,255,0.14);
                box-shadow: 0 18px 44px rgba(15, 23, 42, 0.22);
            }
            .hero-wrap h1 {
                margin: 0 0 0.4rem 0;
                font-size: 2.25rem;
                letter-spacing: -0.03em;
            }
            .hero-wrap p {
                margin: 0;
                max-width: 940px;
                opacity: 0.94;
                line-height: 1.55;
            }
            .section-title {
                font-size: 1.15rem;
                font-weight: 800;
                margin: 1.6rem 0 0.7rem;
                color: #0f172a;
            }
            .insight-box {
                padding: 1rem 1.1rem;
                border-radius: 18px;
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
        <div class="hero-wrap">
            <h1>INEP + indicadores étnicos por UF</h1>
            <p>
                As análises abaixo cruzam os microdados do Censo da Educação Superior com a dimensão demográfica sintética por UF.
                O join é feito em DuckDB, com agregação prévia no nível certo para evitar explosão de linhas e manter a navegação fluida.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Preparando agregações em DuckDB..."):
        raw_data = load_data()
        transformed = transform_data(raw_data)
        kpis = create_kpis(transformed)
        charts = create_charts(transformed)

    st.markdown("<div class='section-title'>KPIs analíticos</div>", unsafe_allow_html=True)
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        _render_kpi("Total de matrículas", _format_number(kpis["total_matriculas"]), "Volume consolidado do ensino superior")
    with kpi_cols[1]:
        _render_kpi("Total de ingressantes", _format_number(kpis["total_ingressantes"]), "Entrada acumulada no período analisado")
    with kpi_cols[2]:
        _render_kpi("Total de concluintes", _format_number(kpis["total_concluintes"]), "Saída acumulada do sistema")
    with kpi_cols[3]:
        _render_kpi("Região com maior acesso", kpis["regiao_maior_acesso"], f"{kpis['taxa_acesso_regiao']:.1f} matrículas por 100 mil habitantes")
    with kpi_cols[4]:
        _render_kpi("Estado com maior concentração", kpis["estado_maior_concentracao_sigla"], kpis["estado_maior_concentracao"])

    st.markdown("<div class='section-title'>1. Modalidade de ensino por região</div>", unsafe_allow_html=True)
    st.plotly_chart(charts["modalidade"], use_container_width=True)
    st.markdown(
        "<div class='insight-box'>"
        "A leitura compara EAD e presencial por região, mas traz no hover o percentual médio de população parda para reforçar a relação entre perfil demográfico e estrutura de oferta."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-title'>2. Heatmap de acesso ao ensino superior</div>", unsafe_allow_html=True)
    st.plotly_chart(charts["heatmap"], use_container_width=True)
    st.markdown(
        "<div class='insight-box'>"
        "Os intensities são ponderados pela participação demográfica de cada grupo, o que ajuda a localizar regiões em que ingresso e conclusão tendem a concentrar-se em perfis raciais distintos."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-title'>3. Mapa choropleth do Brasil</div>", unsafe_allow_html=True)
    st.plotly_chart(charts["mapa"], use_container_width=True)
    st.markdown(
        "<div class='insight-box'>"
        "O mapa usa a sigla da UF como chave geográfica e inclui matrículas, renda, IDH e composição racial no tooltip, permitindo comparação rápida entre intensidade educacional e contexto social."
        "</div>",
        unsafe_allow_html=True,
    )

 
    from src.pages.integrada_inep_etnia.business import GRUPOS_ETNICOS, get_etnia_dinamica
    from src.pages.integrada_inep_etnia.components import render_grafico_dinamico

    st.markdown("<div class='section-title'>4. Análise dinâmica por autodeclaração racial</div>", unsafe_allow_html=True)

    uf_df = transformed["uf"].copy()
    etnia_long = get_etnia_dinamica(uf_df)

    regioes_disponiveis = sorted(uf_df["REGIAO"].dropna().unique().tolist())
    grupos_disponiveis = list(GRUPOS_ETNICOS.keys())

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        regiao_sel = st.selectbox(
            "Região",
            options=["Todas"] + regioes_disponiveis,
            index=0,
            key="dinamico_regiao",
        )

    with filter_col2:
        if regiao_sel == "Todas":
            estados_opts = sorted(uf_df["UF_NOME"].dropna().unique().tolist())
        else:
            estados_opts = sorted(
                uf_df.loc[uf_df["REGIAO"] == regiao_sel, "UF_NOME"].dropna().unique().tolist()
            )
        estado_sel = st.selectbox(
            "Estado (UF)",
            options=["Todos"] + estados_opts,
            index=0,
            key="dinamico_estado",
        )

    with filter_col3:
        grupo_sel = st.selectbox(
            "Autodeclaração racial",
            options=["Todas"] + grupos_disponiveis,
            index=0,
            key="dinamico_grupo",
        )

    df_filtrado = etnia_long.copy()

    if regiao_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["REGIAO"] == regiao_sel]

    if estado_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["UF_NOME"] == estado_sel]

    if grupo_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["GRUPO_ETNICO"] == grupo_sel]

    if estado_sel != "Todos":
        x_col = "UF_NOME"
        barmode = "group"
        nivel = estado_sel
    elif regiao_sel != "Todas":
        x_col = "UF_NOME"
        barmode = "group"
        nivel = regiao_sel
    else:
        df_filtrado = (
            df_filtrado.groupby(["REGIAO", "GRUPO_ETNICO"], as_index=False)
            .agg(POPULACAO_EST=("POPULACAO_EST", "sum"), PERC_NO_TOTAL=("PERC_NO_TOTAL", "mean"))
        )
        df_filtrado["UF_NOME"] = df_filtrado["REGIAO"]
        x_col = "REGIAO"
        barmode = "group"
        nivel = "Brasil"

    barmode = "stack" if grupo_sel == "Todas" and estado_sel == "Todos" and regiao_sel == "Todas" else "group"

    partes_titulo = []
    if regiao_sel != "Todas":
        partes_titulo.append(f"Região: {regiao_sel}")
    if estado_sel != "Todos":
        partes_titulo.append(f"Estado: {estado_sel}")
    if grupo_sel != "Todas":
        partes_titulo.append(f"Grupo: {grupo_sel}")
    titulo_grafico = "Distribuição por autodeclaração racial"
    if partes_titulo:
        titulo_grafico += " — " + " | ".join(partes_titulo)

    fig_dinamico = render_grafico_dinamico(df_filtrado, x_col=x_col, titulo=titulo_grafico, barmode=barmode)
    st.plotly_chart(fig_dinamico, use_container_width=True)


if __name__ == "__main__":
    main()
