import pandas as pd
from src.database import get_db


class PerformanceService:
    """Regra de Negócio para Performance de Cursos e Social """
    @staticmethod
    def get_top_10_curso() -> pd.DataFrame:
        """Os 10 cursos com maiores números de matriculados"""
        db = get_db()
        data_path = db.get_data_path()

        query = f"""
        SELECT NO_CURSO, 
               SUM(QT_MAT) AS total_matriculados
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        GROUP BY NO_CURSO
        ORDER BY total_matriculados DESC
        LIMIT 10
        """
        df_top_10 = db.execute_query(query).df()
        return df_top_10.sort_values(by='total_matriculados', ascending=True)
    
    @staticmethod
    def get_financiamento_comparativo() -> pd.DataFrame:
        """Comparativo de matrículas entre FIES, PROUNI Integral e PROUNI Parcial"""
        db = get_db()
        data_path = db.get_data_path()

        query = f"""
        SELECT 
            SUM(QT_MAT_FIES) AS FIES,
            SUM(QT_MAT_PROUNII) AS PROUNI_Integral,
            SUM(QT_MAT_PROUNIP) AS PROUNI_Parcial
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        """
        
        df_result = db.execute_query(query).df()
        
        df_melted = df_result.melt(var_name='Programa', value_name='Total_Matriculas')
        
        return df_melted
    @staticmethod
    def get_ingresso_comparativo() -> pd.DataFrame:
        """Regra de Negócio: Comparativo de ingressantes via ENEM vs VESTIBULAR"""
        db = get_db()
        data_path = db.get_data_path()

        query = f"""
        SELECT 
            SUM(QT_ING_ENEM) AS ENEM,
            SUM(QT_ING_VESTIBULAR) AS VESTIBULAR
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        """
        
        df_result = db.execute_query(query).df()
        
        df_melted = df_result.melt(
            var_name='Forma_Ingresso', 
            value_name='Total_Ingressantes'
        )
        
        return df_melted
    @staticmethod
    def get_conclusao_hierarquia() -> pd.DataFrame:
        db = get_db()
        data_path = db.get_data_path()

        query = f"""
        SELECT 
            NO_REGIAO AS Regiao,
            NO_CURSO AS Curso,
            SUM(QT_CONC) AS Total_Concluintes,
            SUM(QT_ING) AS Total_Ingressantes,
            CASE 
                WHEN SUM(QT_ING) > 0 
                THEN (CAST(SUM(QT_CONC) AS FLOAT) / SUM(QT_ING)) * 100 
                ELSE 0 
            END AS Taxa_Conclusao
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        WHERE NO_REGIAO IS NOT NULL AND NO_CURSO IS NOT NULL
        GROUP BY NO_REGIAO, NO_CURSO
        HAVING Total_Ingressantes > 50 
        ORDER BY Regiao, Taxa_Conclusao DESC
        """
        
        df = db.execute_query(query).df()
        
        df = df.dropna(subset=['Regiao', 'Curso'])
        df = df[(df['Regiao'] != '') & (df['Curso'] != '')]
        
        df['Taxa_Conclusao'] = df['Taxa_Conclusao'].clip(upper=100)
        
        return df
   




    

