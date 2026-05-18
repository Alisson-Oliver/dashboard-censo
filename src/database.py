import duckdb
import os
import re


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados DuckDB"""
    
    def __init__(self):
        self.conn = duckdb.connect()
        self.data_path = self._get_data_path()
        self.etnia_path = self._get_etnia_path()
        self._run_etl_pipeline()
        self._configure_duckdb()
        self._load_data_once()

    def _run_etl_pipeline(self) -> None:
        try:
            from pipeline.etl import run_pipeline
            run_pipeline()
        except Exception:
            pass

    def _configure_duckdb(self):
        """Aplica configurações de desempenho no DuckDB."""
        self.conn.execute("PRAGMA enable_object_cache")
        self.conn.execute("PRAGMA threads=4")

    def _load_data_once(self):
        """Carrega os dados em tabelas temporárias DuckDB.

        Prefere Parquet pré-gerado pelo pipeline ETL quando disponível,
        pois é mais rápido para leitura. Recorre ao CSV original como fallback.
        """
        parquet_censo = self._get_processed_path("censo_agregado.parquet")
        if os.path.exists(parquet_censo):
            censo_source = f"read_parquet('{parquet_censo}')"
        else:
            censo_source = f"read_csv('{self.data_path}', delim=';', encoding='latin-1')"

        self.conn.execute(
            f"""
            CREATE OR REPLACE TEMP TABLE censo_data AS
            SELECT * FROM {censo_source}
            """
        )
        self.conn.execute(
            f"""
            CREATE OR REPLACE TEMP TABLE dim_etnia AS
            SELECT *
            FROM read_csv('{self.etnia_path}', delim=',', header=true)
            """
        )

        self._load_precomputed_tables()

    def _load_precomputed_tables(self) -> None:
        """Carrega tabelas pré-agregadas pelo pipeline ETL quando disponíveis."""
        mapping = {
            "censo_etnia_uf": "censo_etnia_uf.parquet",
            "censo_etnia_regiao": "censo_etnia_regiao.parquet",
            "censo_etnia_modalidade": "censo_etnia_modalidade.parquet",
        }
        for table_name, filename in mapping.items():
            path = self._get_processed_path(filename)
            if os.path.exists(path):
                self.conn.execute(
                    f"""
                    CREATE OR REPLACE TEMP TABLE {table_name} AS
                    SELECT * FROM read_parquet('{path}')
                    """
                )

    def _get_processed_path(self, filename: str) -> str:
        """Retorna o caminho absoluto de um arquivo em data/processed/."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, "data", "processed", filename)

    def _optimize_query(self, query: str) -> str:
        """Substitui leituras diretas do CSV pela tabela temporária em memória."""
        return re.sub(r"FROM\s+read_csv\([^\)]*\)", "FROM censo_data", query, flags=re.IGNORECASE)
    
    @staticmethod
    def _get_data_path():
        """Obtém o caminho absoluto do arquivo data.csv"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'data', 'data.csv')

    @staticmethod
    def _get_etnia_path():
        """Obtém o caminho absoluto do arquivo dim_etnia.csv"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate_path = os.path.join(base_path, 'data', 'dim_etnia.csv')
        if os.path.exists(candidate_path):
            return candidate_path

        return os.path.join(base_path, 'data', 'dados_demograficos_brasil_uf.csv')
    
    def execute_query(self, query: str) -> object:
        """Executa uma query e retorna o resultado"""
        optimized_query = self._optimize_query(query)
        return self.conn.execute(optimized_query)

    def get_table_columns(self, table_name: str) -> list[str]:
        """Retorna as colunas disponíveis de uma tabela temporária."""
        rows = self.conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
        return [row[1] for row in rows]

    def resolve_column(self, table_name: str, candidates: list[str]) -> str:
        """Encontra automaticamente a melhor coluna equivalente disponível."""
        columns = self.get_table_columns(table_name)
        normalized_columns = {self._normalize_identifier(column): column for column in columns}

        for candidate in candidates:
            if candidate in columns:
                return candidate

        for candidate in candidates:
            normalized_candidate = self._normalize_identifier(candidate)
            if normalized_candidate in normalized_columns:
                return normalized_columns[normalized_candidate]

        raise KeyError(f"Nenhuma das colunas {candidates} foi encontrada em {table_name}")

    @staticmethod
    def _normalize_identifier(value: str) -> str:
        """Normaliza nomes de colunas para comparação por equivalência."""
        return re.sub(r"[^a-z0-9]+", "", value.lower())
    
    def get_data_path(self) -> str:
        """Retorna o caminho do arquivo de dados"""
        return self.data_path

    def get_etnia_path(self) -> str:
        """Retorna o caminho do arquivo de dimensão étnica"""
        return self.etnia_path
    
    def close(self):
        """Fecha a conexão"""
        self.conn.close()


_db = None


def get_db() -> DatabaseConnection:
    """Retorna a instância global do banco de dados"""
    global _db
    if _db is None:
        _db = DatabaseConnection()
    return _db
