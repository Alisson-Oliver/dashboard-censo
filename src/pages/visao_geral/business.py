import pandas as pd
from src.database import get_db


class VisaoGeralService:
    """Serviço de negócio para Visão Geral e Distribuição Geográfica"""
    
    @staticmethod
    def get_matriculas_por_regiao(ano: int = None) -> pd.DataFrame:
        """Obtém distribuição de alunos matriculados por região"""
        db = get_db()
        data_path = db.get_data_path()
        
        filtro_ano = f"WHERE NU_ANO_CENSO = {ano}" if ano else ""
        
        query = f"""
        SELECT NO_REGIAO,
               SUM(QT_MAT) AS total_matriculados,
               COUNT(DISTINCT CO_IES) AS quantidade_instituicoes
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        {filtro_ano}
        GROUP BY NO_REGIAO
        ORDER BY total_matriculados DESC
        """
        
        return db.execute_query(query).df()
    
    @staticmethod
    def get_matriculas_por_estado(ano: int = None) -> pd.DataFrame:
        """Obtém distribuição de alunos por estado (para mapa geográfico)"""
        db = get_db()
        data_path = db.get_data_path()
        
        filtro_ano = f"WHERE NU_ANO_CENSO = {ano}" if ano else ""
        
        query = f"""
        SELECT SG_UF,
               NO_UF,
               SUM(QT_MAT) AS total_matriculados
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        {filtro_ano}
        GROUP BY SG_UF, NO_UF
        ORDER BY total_matriculados DESC
        """
        
        return db.execute_query(query).df()
    
    @staticmethod
    def get_instituicoes_por_regiao(ano: int = None) -> pd.DataFrame:
        """Obtém quantidade de instituições de ensino por região"""
        db = get_db()
        data_path = db.get_data_path()
        
        filtro_ano = f"WHERE NU_ANO_CENSO = {ano}" if ano else ""
        
        query = f"""
        SELECT NO_REGIAO,
               COUNT(DISTINCT CO_IES) AS quantidade_instituicoes
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        {filtro_ano}
        GROUP BY NO_REGIAO
        ORDER BY quantidade_instituicoes DESC
        """
        
        return db.execute_query(query).df()
    
    @staticmethod
    def get_matriculas_por_categoria(ano: int = None) -> pd.DataFrame:
        """Obtém distribuição de matrículas por categoria administrativa"""
        db = get_db()
        data_path = db.get_data_path()
        
        filtro_ano = f"AND NU_ANO_CENSO = {ano}" if ano else ""
        
        query = f"""
        SELECT CASE
             WHEN TP_REDE = 1 THEN 'Pública'
             WHEN TP_REDE = 2 THEN 'Privada'
               END AS categoria,
               SUM(QT_MAT) AS total_matriculados
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        WHERE TP_REDE IN (1, 2)
        {filtro_ano}
        GROUP BY 1
        """
        
        return db.execute_query(query).df()
    
    @staticmethod
    def get_matriculas_por_modalidade(ano: int = None) -> pd.DataFrame:
        """Obtém distribuição por modalidade (Presencial/EAD)"""
        db = get_db()
        data_path = db.get_data_path()
        
        filtro_ano = f"WHERE NU_ANO_CENSO = {ano}" if ano else ""
        
        query = f"""
         SELECT CASE
               WHEN TP_MODALIDADE_ENSINO = 1 THEN 'Presencial'
               WHEN TP_MODALIDADE_ENSINO = 2 THEN 'EAD'
             END AS TP_MODALIDADE_ENSINO,
               SUM(QT_MAT) AS total_matriculados
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        {filtro_ano}
         GROUP BY 1
        ORDER BY total_matriculados DESC
        """
        
        return db.execute_query(query).df()
    
    @staticmethod
    def get_anos_disponiveis() -> list:
        """Retorna anos disponíveis no dataset"""
        db = get_db()
        data_path = db.get_data_path()
        
        query = f"""
        SELECT DISTINCT NU_ANO_CENSO
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        ORDER BY NU_ANO_CENSO DESC
        """
        
        result = db.execute_query(query).df()
        return sorted(result['NU_ANO_CENSO'].tolist(), reverse=True)
