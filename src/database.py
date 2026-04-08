import duckdb
import os
import re


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados DuckDB"""
    
    def __init__(self):
        self.conn = duckdb.connect()
        self.data_path = self._get_data_path()
        self._configure_duckdb()
        self._load_data_once()

    def _configure_duckdb(self):
        """Aplica configurações de desempenho no DuckDB."""
        self.conn.execute("PRAGMA enable_object_cache")

    def _load_data_once(self):
        """Carrega o CSV em uma tabela temporária para evitar releitura em cada query."""
        self.conn.execute(
            f"""
            CREATE OR REPLACE TEMP TABLE censo_data AS
            SELECT *
            FROM read_csv('{self.data_path}', delim=';', encoding='latin-1')
            """
        )

    def _optimize_query(self, query: str) -> str:
        """Substitui leituras diretas do CSV pela tabela temporária em memória."""
        return re.sub(r"FROM\s+read_csv\([^\)]*\)", "FROM censo_data", query, flags=re.IGNORECASE)
    
    @staticmethod
    def _get_data_path():
        """Obtém o caminho absoluto do arquivo data.csv"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'data', 'data.csv')
    
    def execute_query(self, query: str) -> object:
        """Executa uma query e retorna o resultado"""
        optimized_query = self._optimize_query(query)
        return self.conn.execute(optimized_query)
    
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
