import pandas as pd
from src.database import get_db


class FluxoAcademicoService:
    """Serviço de negócio para Fluxo Acadêmico"""
    
    @staticmethod
    def get_funil_fluxo_2024() -> pd.Series:
        """Obtém dados do funil de fluxo acadêmico para 2024"""
        db = get_db()
        data_path = db.get_data_path()
        
        query = f"""
        SELECT
            SUM(QT_ING) AS ingressantes,
            SUM(QT_MAT) AS matriculados,
            SUM(QT_CONC) AS concluintes
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        WHERE NU_ANO_CENSO = 2024
        """
        
        return db.execute_query(query).df().iloc[0]
    
    @staticmethod
    def get_fluxo_por_regiao_2024() -> pd.DataFrame:
        """Obtém fluxo acadêmico por região para 2024"""
        db = get_db()
        data_path = db.get_data_path()
        
        query = f"""
        SELECT NO_REGIAO,
               SUM(QT_ING) AS ingressantes,
               SUM(QT_MAT) AS matriculados,
               SUM(QT_CONC) AS concluintes
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        WHERE NU_ANO_CENSO = 2024
        GROUP BY NO_REGIAO
        ORDER BY NO_REGIAO
        """
        
        return db.execute_query(query).df()
    
    @staticmethod
    def get_taxa_conclusao_por_curso() -> pd.DataFrame:
        """Calcula taxa de conclusão por curso"""
        db = get_db()
        data_path = db.get_data_path()
        
        query = f"""
        SELECT NO_CURSO,
               SUM(QT_CONC) AS total_concluintes,
               SUM(QT_MAT) AS total_matriculados,
               (SUM(QT_CONC) / SUM(QT_MAT)) * 100 AS taxa_conclusao
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        GROUP BY NO_CURSO
        HAVING SUM(QT_MAT) > 0
        """
        
        return db.execute_query(query).df()
    
    @staticmethod
    def get_top_cursos_menor_taxa(limit: int = 10) -> pd.DataFrame:
        """Obtém top cursos com menor taxa de conclusão"""
        df = FluxoAcademicoService.get_taxa_conclusao_por_curso()
        return df.sort_values("taxa_conclusao", ascending=True).head(limit)
    
    @staticmethod
    def get_top_cursos_maior_taxa(limit: int = 10) -> pd.DataFrame:
        """Obtém top cursos com maior taxa de conclusão"""
        df = FluxoAcademicoService.get_taxa_conclusao_por_curso()
        return df.sort_values("taxa_conclusao", ascending=False).head(limit)
    
    @staticmethod
    def get_estatisticas_taxa_conclusao() -> dict:
        """Retorna estatísticas das taxas de conclusão"""
        df = FluxoAcademicoService.get_taxa_conclusao_por_curso()
        
        return {
            "media": df['taxa_conclusao'].mean(),
            "mediana": df['taxa_conclusao'].median(),
            "minimo": df['taxa_conclusao'].min(),
            "maximo": df['taxa_conclusao'].max(),
            "cursos_0_pct": (df['taxa_conclusao'] == 0).sum(),
            "cursos_100_pct": (df['taxa_conclusao'] == 100).sum(),
        }
