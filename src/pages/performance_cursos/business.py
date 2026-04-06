import pandas as pd
from src.database import get_db


class PerformanceService:
    """Regra de Negócio para Performance de Cursos e Social """
    @staticmethod
    def get_top_10_curso() -> pd.DataFrame:
        """Os 10 cursos com maiores números de matriculados"""
        #Conexão com o banco
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
    
    ###########################################################################
    ###-----PROGRAMAS DE FINANCIAMENTO------############################
    @staticmethod
    def get_financiamento_comparativo() -> pd.DataFrame:
        """Comparativo de matrículas entre FIES, PROUNI Integral e PROUNI Parcial"""
        db = get_db()
        data_path = db.get_data_path()

        #Somamos as colunas específicas de financiamento
        query = f"""
        SELECT 
            SUM(QT_MAT_FIES) AS FIES,
            SUM(QT_MAT_PROUNII) AS PROUNI_Integral,
            SUM(QT_MAT_PROUNIP) AS PROUNI_Parcial
        FROM read_csv('{data_path}', delim=';', encoding='latin-1')
        """
        
        #Executa e transforma em DataFrame
        df_result = db.execute_query(query).df()
        
        #Transformamos o formato de colunas para linhas para facilitar o gráfico de barras
        df_melted = df_result.melt(var_name='Programa', value_name='Total_Matriculas')
        
        return df_melted
    #################################################################################


    

