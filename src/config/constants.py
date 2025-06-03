"""Módulo de definição de constantes globais para o projeto."""

from pathlib import Path
from zoneinfo import ZoneInfo

APP_NAME: str = "py-ai-api-integration"
"""Nome da aplicação: `py-ai-api-integration`."""

VERSION: str = "0.1.0"
"""Versão da aplicação: `0.1.0`"""

SETTINGS_FILE: Path = Path("./src/config/settings.yaml")
"""Caminho para o arquivo de configuração global: `./src/config/settings.yaml`"""

BRT: ZoneInfo = ZoneInfo("America/Sao_Paulo")
"""Define o objeto de fuso horário para o horário de Brasília: `America/Sao_Paulo`"""
