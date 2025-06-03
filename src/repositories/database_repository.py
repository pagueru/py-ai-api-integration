"""Módulo para persistência de uso da API DeepSeek via SQLite."""

from datetime import datetime
import logging
import sqlite3
from typing import Any, NamedTuple

import pandas as pd

from src.config.constants import BRT
from src.core.base_class import BaseClass

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class UsageRecord(NamedTuple):
    """Registro de uso da API DeepSeek."""

    usage_id: str
    created: int
    model: str
    system_fingerprint: str | None
    prompt: str
    completion: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_tokens: int = 0
    cache_hit_tokens: int = 0
    cache_miss_tokens: int = 0
    finish_reason: str | None = None
    logprobs: Any = None


class SQLiteRepository(BaseClass):
    """Classe para persistência de uso da API DeepSeek via SQLite."""

    def __init__(self, db_path: str | None = None) -> None:
        """Inicializa o repositório SQLite."""
        self.db_path = db_path if db_path else "api_usage.db"
        """Cria a conexão e a tabela se não existir."""

        self._create_table()

    def _format_timestamp(self, timestamp: float) -> str:
        """Formata um timestamp em uma string legível."""
        return datetime.fromtimestamp(timestamp, tz=BRT).strftime("%Y-%m-%d %H:%M:%S %z")

    def get_connection(self) -> sqlite3.Connection:
        """Retorna conexão com o banco de dados."""
        return sqlite3.connect(self.db_path)

    def _create_table(self) -> None:
        """Cria a tabela de uso da API se não existir."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS api_usages (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            model TEXT NOT NULL,
            system_fingerprint TEXT,
            prompt TEXT NOT NULL,
            completion TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL,
            completion_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            cached_tokens INTEGER DEFAULT 0,
            cache_hit_tokens INTEGER DEFAULT 0,
            cache_miss_tokens INTEGER DEFAULT 0,
            finish_reason TEXT,
            logprobs TEXT
        );
        """
        create_indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_model ON api_usages(model);",
            "CREATE INDEX IF NOT EXISTS idx_created_at ON api_usages(created_at);",
        ]
        try:
            with self.get_connection() as conn:
                conn.execute(create_table_sql)
                for sql in create_indexes_sql:
                    conn.execute(sql)
                conn.commit()
                logger.info("Tabela e índices criados com sucesso.")
        except sqlite3.Error:
            logger.exception("Erro ao criar tabela no banco de dados.")
            raise

    def insert_usage(self, record: UsageRecord) -> None:
        """Insere um registro de uso no banco de dados."""
        created_at = self._format_timestamp(record.created)
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO api_usages (
                        id, created_at, model, system_fingerprint, prompt, completion,
                        prompt_tokens, completion_tokens, total_tokens,
                        cached_tokens, cache_hit_tokens, cache_miss_tokens,
                        finish_reason, logprobs
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.usage_id,
                        created_at,
                        record.model,
                        record.system_fingerprint,
                        record.prompt,
                        record.completion,
                        record.prompt_tokens,
                        record.completion_tokens,
                        record.total_tokens,
                        record.cached_tokens,
                        record.cache_hit_tokens,
                        record.cache_miss_tokens,
                        record.finish_reason,
                        str(record.logprobs) if record.logprobs is not None else None,
                    ),
                )
                conn.commit()
                logger.info("Registro inserido com sucesso.")
        except sqlite3.Error:
            logger.exception("Erro ao inserir registro no banco de dados.")
            raise

    def fetch_records_as_dataframe(self, limit: int | None = None) -> pd.DataFrame:
        """Retorna registros como DataFrame."""
        try:
            with self.get_connection() as connection:
                query = "SELECT * FROM api_usages"
                if limit:
                    query += f" LIMIT {limit}"
                return pd.read_sql_query(query, connection)
        except sqlite3.Error:
            logger.exception("Erro ao realizar consulta no banco de dados.")
            return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

    def get_usage_stats(self) -> dict[str, Any]:
        """Retorna estatísticas de uso da API."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Total de requisições
                cursor.execute("SELECT COUNT(*) FROM api_usages")
                total_requests = cursor.fetchone()[0]

                # Total de tokens
                cursor.execute("SELECT SUM(total_tokens) FROM api_usages")
                total_tokens = cursor.fetchone()[0] or 0

                # Requisições por modelo
                cursor.execute("""
                    SELECT model, COUNT(*) as count
                    FROM api_usages
                    GROUP BY model
                """)
                models_usage = dict(cursor.fetchall())

                return {
                    "total_requests": total_requests,
                    "total_tokens": total_tokens,
                    "models_usage": models_usage,
                }
        except sqlite3.Error:
            logger.exception("Erro ao obter estatísticas.")
            return {}
