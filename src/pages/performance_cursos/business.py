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


    

