"""Módulo base para todas as classes do projeto."""

from dataclasses import dataclass
import inspect
from pathlib import Path
import shutil
from typing import Any

import yaml

from src.common.echo import echo
from src.config.constypes import PathLike
from src.core.errors import ProjectError


@dataclass
class BaseClass:
    """Classe base para fornecer métodos comuns a todas as classes."""

    def _get_current_method_name(self) -> str:
        """Retorna dinamicamente o nome da classe e do método atual."""
        try:
            current_frame = inspect.currentframe()
            if current_frame is not None:
                method_name = current_frame.f_code.co_name
                return f"{self.__class__.__name__}.{method_name}"
        except ProjectError:
            echo("Falha ao obter o nome do método atual.", "error")
            raise
        else:
            return f"{self.__class__.__name__}.<desconhecido>"

    def _raise_error(self) -> str:
        """Levanta um erro personalizado com o nome da classe e do método atual."""
        return f"Erro inesperado ao executar o método '{self._get_current_method_name()}'"

    def _separator_line(self, char: str = "-", padding: int = 0) -> None:
        """Imprime uma linha ajustada ao tamanho do terminal ou ao valor fornecido pelo usuário."""
        try:
            width = padding if padding > 0 else shutil.get_terminal_size((80, 20)).columns
            print(char * width)
        except ProjectError as exc:
            echo(f"Falha ao obter o tamanho do terminal: {exc}", "warn")
            raise

    def _ensure_path(self, path_str: PathLike) -> Path:
        """Converte uma string de caminho em um objeto Path e garante que o diretório exista."""
        if not isinstance(path_str, (str, Path)):
            msg = "O caminho deve ser uma string ou um objeto Path."
            echo(msg, "error")
            raise ProjectError(msg)
        path = Path(path_str)
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except ProjectError as exc:
                echo(f"Erro ao criar diretório: {exc}", "error")
                raise
        return path

    def _load_yaml(self, file_path: PathLike, key: str | None = None) -> dict[str, Any]:
        """Carrega um dicionário a partir de um arquivo YAML."""
        try:
            file_path = Path(file_path)
            with file_path.open("r", encoding="utf-8") as file:
                settings: dict[str, Any] = yaml.safe_load(file)
                return settings[key] if key else settings
        except FileNotFoundError as exc:
            echo(f"Arquivo de configurações não encontrado: {exc}", "error")
            raise
        except ProjectError as exc:
            echo(f"Erro ao carregar o arquivo YAML: {exc}", "error")
            raise
