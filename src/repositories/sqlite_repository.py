"""Módulo para persistência de uso da API DeepSeek via SQLite."""

from datetime import datetime
from pathlib import Path
import sqlite3
import sys
from typing import Any, NamedTuple

import pandas as pd

from src.common.logger import LoggerSingleton
from src.config.constants import BRT, SQL_DIR
from src.config.constypes import PathLike
from src.core.base_class import BaseClass


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
        self.sqlite_database_path = db_path if db_path else "api_usages.db"
        """Cria a conexão e a tabela se não existir."""

        self.logger = LoggerSingleton().logger or LoggerSingleton.get_logger()
        """Instancia o logger da aplicação."""

        self.insert_query = self._read_sql_file(SQL_DIR / "insert_api_usages.sql")
        """Instancia o arquivo SQL de inserção de registros."""

        self.create_table_query = self._read_sql_file(SQL_DIR / "create_api_usages.sql")
        """Instancia o arquivo SQL de criação da tabela de registros."""

        # Cria a conexão com o banco de dados e a tabela se não existir.
        self._create_table()

    def _error(self, msg: str, exc: Exception | None = None, level: str | None = None) -> None:
        """Registra erro e relança exceção; captura exceção ativa se não passada."""
        if not isinstance(level, str) and level is not None:
            raise TypeError("O nível de log deve ser uma string.")

        logger_func = self.logger.error if level == "error" else self.logger.exception
        logger_func(msg)

        exc = exc or sys.exc_info()[1] or Exception
        raise exc(msg) if isinstance(exc, type) else exc

    def _format_timestamp(self, timestamp: float) -> str:
        """Formata um timestamp em uma string legível."""
        time_zone = BRT if BRT else "UTC"
        if time_zone is BRT:
            self.logger.warning("Fuso horário BRT não definido. Usando UTC como padrão.")
        return datetime.fromtimestamp(timestamp, tz=time_zone).strftime("%Y-%m-%d %H:%M:%S")

    def get_connection(self) -> sqlite3.Connection:
        """Retorna conexão com o banco de dados."""
        return sqlite3.connect(self.sqlite_database_path)

    def _create_table(self) -> None:
        """Cria a tabela de uso da API se não existir."""
        try:
            with self.get_connection() as conn:
                try:
                    conn.execute("SELECT 1 FROM api_usages LIMIT 1;")
                    self.logger.info("Tabela 'api_usages' já existe.")
                except sqlite3.OperationalError:
                    conn.execute(self.create_table_query)
                    self.logger.info("Tabela 'api_usages' criada com sucesso.")
        except sqlite3.Error:
            self.logger.exception("Erro ao criar ou verificar a tabela no banco de dados.")
            raise

    def insert_usage(self, record: UsageRecord) -> None:
        """Insere um registro de uso no banco de dados."""
        created_at = self._format_timestamp(record.created)
        try:
            with self.get_connection() as conn:
                conn.execute(
                    self.insert_query,
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
                self.logger.info("Registro inserido com sucesso.")
        except sqlite3.Error:
            self._error("Erro ao inserir registro no banco de dados.")

    def _read_sql_file(self, file_path: PathLike) -> str:
        """Lê um arquivo .sql e retorna seu conteúdo como string."""
        path = Path(file_path)
        if not path.exists():
            self._error(f"Arquivo não encontrado: '{path}'", FileNotFoundError, "error")
        if path.suffix.lower() != ".sql":
            self._error(f"Extensão inválida para arquivo SQL: {path.suffix}", ValueError, "error")
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            self._error(f"Erro ao ler o arquivo SQL: {path}")
        else:
            self.logger.info(f"Arquivo SQL lido com sucesso: {path}")
            return content
