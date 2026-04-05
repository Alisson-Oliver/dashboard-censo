import duckdb
import os


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados DuckDB"""
    
    def __init__(self):
        self.conn = duckdb.connect()
        self.data_path = self._get_data_path()
    
    @staticmethod
    def _get_data_path():
        """Obtém o caminho absoluto do arquivo data.csv"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'data', 'data.csv')
    
    def execute_query(self, query: str) -> object:
        """Executa uma query e retorna o resultado"""
        return self.conn.execute(query)
    
    def get_data_path(self) -> str:
        """Retorna o caminho do arquivo de dados"""
        return self.data_path
    
    def close(self):
        """Fecha a conexão"""
        self.conn.close()


# Instância global de conexão
_db = None


def get_db() -> DatabaseConnection:
    """Retorna a instância global do banco de dados"""
    global _db
    if _db is None:
        _db = DatabaseConnection()
    return _db
