import pandas as pd

from src.database import get_db


class PerfilSocioeconomicoService:
    """Serviço de negócio para o perfil socioeconômico do estudante."""

    @staticmethod
    def _query_melted(columns: list[tuple[str, str]], ano: int = None) -> pd.DataFrame:
        db = get_db()
        data_path = db.get_data_path()
        filtro_ano = f"WHERE NU_ANO_CENSO = {ano}" if ano else ""
        select_clause = ",\n               ".join([f'SUM({coluna}) AS "{alias}"' for coluna, alias in columns])

        query = f"""
        SELECT {select_clause}
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        {filtro_ano}
        """

        df = db.execute_query(query).df().fillna(0)
        return df.melt(var_name="categoria", value_name="total")

    @staticmethod
    def get_anos_disponiveis() -> list[int]:
        db = get_db()
        data_path = db.get_data_path()

        query = f"""
        SELECT DISTINCT NU_ANO_CENSO
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        ORDER BY NU_ANO_CENSO DESC
        """

        result = db.execute_query(query).df()
        return sorted(result["NU_ANO_CENSO"].tolist(), reverse=True)

    @staticmethod
    def get_distribuicao_genero(ano: int = None) -> pd.DataFrame:
        df = PerfilSocioeconomicoService._query_melted(
            [
                ("QT_MAT_FEM", "Feminino"),
                ("QT_MAT_MASC", "Masculino"),
            ],
            ano,
        )
        return df[df["total"] > 0]

    @staticmethod
    def get_faixa_etaria(ano: int = None) -> pd.DataFrame:
        df = PerfilSocioeconomicoService._query_melted(
            [
                ("QT_MAT_0_17", "0 a 17 anos"),
                ("QT_MAT_18_24", "18 a 24 anos"),
                ("QT_MAT_25_29", "25 a 29 anos"),
                ("QT_MAT_30_34", "30 a 34 anos"),
                ("QT_MAT_35_39", "35 a 39 anos"),
                ("QT_MAT_40_49", "40 a 49 anos"),
                ("QT_MAT_50_59", "50 a 59 anos"),
                ("QT_MAT_60_MAIS", "60 anos ou mais"),
            ],
            ano,
        )
        return df[df["total"] > 0]

    @staticmethod
    def get_raca_cor(ano: int = None) -> pd.DataFrame:
        df = PerfilSocioeconomicoService._query_melted(
            [
                ("QT_MAT_BRANCA", "Branca"),
                ("QT_MAT_PRETA", "Preta"),
                ("QT_MAT_PARDA", "Parda"),
                ("QT_MAT_AMARELA", "Amarela"),
                ("QT_MAT_INDIGENA", "Indígena"),
                ("QT_MAT_CORND", "Não declarada"),
            ],
            ano,
        )
        return df[df["total"] > 0]

    @staticmethod
    def get_deficiencia(ano: int = None) -> pd.DataFrame:
        db = get_db()
        data_path = db.get_data_path()
        filtro_ano = f"WHERE NU_ANO_CENSO = {ano}" if ano else ""

        query = f"""
        SELECT
            SUM(QT_MAT_DEFICIENTE) AS "Com deficiência",
            CASE
                WHEN SUM(QT_MAT) > SUM(QT_MAT_DEFICIENTE)
                THEN SUM(QT_MAT) - SUM(QT_MAT_DEFICIENTE)
                ELSE 0
            END AS "Sem deficiência"
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        {filtro_ano}
        """

        df = db.execute_query(query).df().fillna(0)
        return df.melt(var_name="categoria", value_name="total")

    @staticmethod
    def get_financiamento(ano: int = None) -> pd.DataFrame:
        df = PerfilSocioeconomicoService._query_melted(
            [
                ("QT_MAT_FIES", "FIES"),
                ("QT_MAT_PROUNII", "PROUNI Integral"),
                ("QT_MAT_PROUNIP", "PROUNI Parcial"),
                ("QT_MAT_FINANC_REEMB_OUTROS", "Outros reembolsáveis"),
                ("QT_MAT_FINANC_NREEMB_OUTROS", "Outros não reembolsáveis"),
            ],
            ano,
        )
        return df[df["total"] > 0]

    @staticmethod
    def get_reserva_vaga(ano: int = None) -> pd.DataFrame:
        df = PerfilSocioeconomicoService._query_melted(
            [
                ("QT_MAT_RESERVA_VAGA", "Total com reserva"),
                ("QT_MAT_RVREDEPUBLICA", "Rede pública"),
                ("QT_MAT_RVPPI", "Pretos, pardos e indígenas"),
                ("QT_MAT_RVQUILO", "Quilombola"),
                ("QT_MAT_RVREFU", "Escola pública federal"),
                ("QT_MAT_RVPOVT", "Baixa renda"),
                ("QT_MAT_RVPDEF", "Pessoa com deficiência"),
                ("QT_MAT_RVSOCIAL_RF", "Renda familiar"),
                ("QT_MAT_RVIDOSO", "Idoso"),
                ("QT_MAT_RVINTERN", "Internacional"),
                ("QT_MAT_RVMEDAL", "Medalhista"),
                ("QT_MAT_RVTRANS", "Transf. de escola pública"),
                ("QT_MAT_RVOUTROS", "Outros critérios"),
            ],
            ano,
        )
        return df[df["total"] > 0]

    @staticmethod
    def get_apoio_social(ano: int = None) -> pd.DataFrame:
        return PerfilSocioeconomicoService._query_melted(
            [
                ("QT_MAT_APOIO_SOCIAL", "Apoio social"),
                ("QT_MAT_ATIV_EXTRACURRICULAR", "Atividades extracurriculares"),
                ("QT_MAT_MOB_ACADEMICA", "Mobilidade acadêmica"),
            ],
            ano,
        )

    @staticmethod
    def get_apoio_social_individual(ano: int = None) -> pd.DataFrame:
        db = get_db()
        data_path = db.get_data_path()
        filtro_ano = f"WHERE NU_ANO_CENSO = {ano}" if ano else ""

        query = f"""
        SELECT
            SUM(QT_MAT_APOIO_SOCIAL) AS "Com apoio social",
            CASE
                WHEN SUM(QT_MAT) > SUM(QT_MAT_APOIO_SOCIAL)
                THEN SUM(QT_MAT) - SUM(QT_MAT_APOIO_SOCIAL)
                ELSE 0
            END AS "Sem apoio social"
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        {filtro_ano}
        """

        df = db.execute_query(query).df().fillna(0)
        return df.melt(var_name="categoria", value_name="total")

    @staticmethod
    def get_atividades_extracurriculares_individual(ano: int = None) -> pd.DataFrame:
        db = get_db()
        data_path = db.get_data_path()
        filtro_ano = f"WHERE NU_ANO_CENSO = {ano}" if ano else ""

        query = f"""
        SELECT
            SUM(QT_MAT_ATIV_EXTRACURRICULAR) AS "Com atividades extracurriculares",
            CASE
                WHEN SUM(QT_MAT) > SUM(QT_MAT_ATIV_EXTRACURRICULAR)
                THEN SUM(QT_MAT) - SUM(QT_MAT_ATIV_EXTRACURRICULAR)
                ELSE 0
            END AS "Sem atividades extracurriculares"
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        {filtro_ano}
        """

        df = db.execute_query(query).df().fillna(0)
        return df.melt(var_name="categoria", value_name="total")

    @staticmethod
    def get_mobilidade_academica_individual(ano: int = None) -> pd.DataFrame:
        db = get_db()
        data_path = db.get_data_path()
        filtro_ano = f"WHERE NU_ANO_CENSO = {ano}" if ano else ""

        query = f"""
        SELECT
            SUM(QT_MAT_MOB_ACADEMICA) AS "Com mobilidade acadêmica",
            CASE
                WHEN SUM(QT_MAT) > SUM(QT_MAT_MOB_ACADEMICA)
                THEN SUM(QT_MAT) - SUM(QT_MAT_MOB_ACADEMICA)
                ELSE 0
            END AS "Sem mobilidade acadêmica"
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        {filtro_ano}
        """

        df = db.execute_query(query).df().fillna(0)
        return df.melt(var_name="categoria", value_name="total")
