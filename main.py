"""Módulo principal da aplicação."""

import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import httpx

from repositories.database_repository import SQLiteRepository, UsageRecord
from src.common.echo import echo
from src.common.logger import LoggerSingleton
from src.config.constants import SETTINGS_FILE
from src.core.base_class import BaseClass

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


class LLMApiClient(BaseClass):
    """Objeto principal da aplicação para interação com a API e persistência dos dados."""

    def __init__(
        self,
        provider: str | None = "deepseek",
        prompt: str | None = None,
        model: str | None = None,
    ) -> None:
        """Inicializa a aplicação."""
        self.settings_config = super()._load_yaml(SETTINGS_FILE)
        """Instancia as configurações do arquivo settings.yaml."""

        self.logger = LoggerSingleton().logger or LoggerSingleton.get_logger()
        """Instancia o logger da aplicação."""

        self.provider_settings: dict[str, str] = self.settings_config["provider_settings"][provider]
        """Instancia o dicionário de configurações de provedores."""

        self.model_settings: dict[str, str] = self.settings_config["model_settings"]
        """Instancia o dicionário de configurações de modelos."""

        self.model = model if model else self.provider_settings["model"]
        """Instancia o modelo a ser utilizado, ex: `deepseek-chat`."""

        self.api_url = self.provider_settings["api_url"]
        """Instancia a URL da API, ex: `https://api.deepseek.com/v1/chat/completions`."""

        self.max_tokens = self.model_settings["max_tokens"]
        """Instancia o número máximo de tokens a serem gerados pela API, ex: `100`."""

        self.temperature = self.model_settings["temperature"]
        """Instancia a temperatura para a geração de texto, ex: `0.7`."""

        self.top_p = self.model_settings["top_p"]
        """Instancia o valor de top_p para a geração de texto, ex: `0.5`."""

        self.system_content = self.model_settings["system_content"]
        """Instancia o comportamento e o papel da IA."""

        self.user_content = prompt if prompt else self.model_settings["user_content"]
        """Instancia o prompt que será respondido pela IA."""

        self.api_key_name = self.provider_settings["api_key_name"]
        """Instancia o nome da variável de ambiente que contém a API key, ex: `DEEPSEEK_API_KEY`."""

        self.api_key = self._get_api_key()
        """Instancia a chave da API a partir das variáveis de ambiente."""

        self.headers = self._create_headers()
        """Instancia os cabeçalhos para a requisição HTTP."""

        self.repo = SQLiteRepository(db_path="./database/api_usage.db")
        """Instancia o repositório SQLite para persistência de uso da API."""

        self.UsageRecord = UsageRecord
        """Instancia o NamedTuple para registro de uso da API."""

    def _handle_value_error(self, error_message: str) -> None:
        """Encapsula o tratamento de ValueError com logging."""
        self.logger.exception(error_message)
        raise ValueError(error_message)

    def _get_api_key(self) -> str:
        """Valida se o nome da chave da API está definida e retorna seu valor."""
        self.logger.info("Obtendo chave da API a partir das variáveis de ambiente.")
        api_key = os.getenv(self.api_key_name)
        if not api_key:
            self._handle_value_error(
                f"{self.api_key_name} não encontrada nas variáveis de ambiente"
            )
        self.logger.info(f"Chave da API '{self.api_key_name}' obtida com sucesso.")
        return api_key

    def _create_payload(self, prompt: str | None = None) -> dict[str, Any]:
        """Cria payload para requisição à API."""
        self.logger.info("Criando payload para o prompt.")
        # TODO: validar se todos os provedores aceitam o mesmo payload.
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": prompt if prompt else self.user_content},
            ],
            # "n": 2,  # Solicita duas respostas
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            # "stream": False,  # Define se a resposta será transmitida em tempo real
        }

    def _create_headers(self) -> dict[str, str]:
        """Retorna os cabeçalhos para a requisição HTTP."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _call_deepseek_api(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self.logger.info(f"Enviando requisição para a API: '{self.api_url.capitalize()}'.")
            # print(payload, self.api_url, self.headers)
            response = httpx.post(self.api_url, headers=self.headers, json=payload, timeout=10.0)
            response.raise_for_status()
            self.logger.info("Resposta recebida com sucesso.")
            return response.json()
        except httpx.HTTPError as e:
            self.logger.exception("Erro na chamada HTTP.")
            return {"error": str(e)}

    # TODO: Melhorar a mensagem de retorno para o usuário
    def format_result_for_user(self, result: dict[str, Any]) -> str:
        """Formata o resultado da API para uma leitura amigável ao usuário."""
        if result["choices"]:
            completion = result["choices"][0]["message"]["content"]
            model = result["model"]
            total_tokens = result["usage"]["total_tokens"]
            prompt = result["prompt"][0]

            super()._separator_line()
            print(f"📌 Prompt: {prompt}")
            print(f"💡 Resposta: {completion}")
            super()._separator_line()
            print("🔍 Detalhes:")
            print(f"   • Modelo: {model}")
            print(f"   • Tokens Utilizados: {total_tokens}")
            formatted_result = ""
        else:
            formatted_result = "A resposta da API não contém os campos esperados."

        return formatted_result

    def json_to_usage_record(self, result: dict[str, Any]) -> UsageRecord:
        """Converte o dicionário de resposta da API em um objeto UsageRecord."""
        usage = result["usage"]
        choice = result["choices"][0]
        return self.UsageRecord(
            usage_id=result["id"],
            created=result["created"],
            model=result["model"],
            system_fingerprint=result["system_fingerprint"],
            prompt=result["choices"],
            completion=choice["message"]["content"],
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            total_tokens=usage["total_tokens"],
            cached_tokens=usage["prompt_tokens_details"]["cached_tokens"],
            cache_hit_tokens=usage["prompt_cache_hit_tokens"],
            cache_miss_tokens=usage["prompt_cache_miss_tokens"],
            finish_reason=choice["finish_reason"],
            logprobs=choice["logprobs"],
        )

    def json_dumps(self, data: dict[str, Any]) -> None:
        """Converte um dicionário em uma string JSON formatada e exibe no console."""
        try:
            print(json.dumps(data, indent=4, ensure_ascii=False))
        except TypeError:
            self.logger.exception("Erro ao converter objeto para JSON.")
            raise

    def run(self, custom_prompt: str | None = None) -> None:
        """Executa uma consulta à API DeepSeek."""
        self.logger.info("Iniciando execução do programa.")
        payload = self._create_payload(prompt=custom_prompt)
        result = self._call_deepseek_api(payload)
        result["prompt"] = self.user_content
        self.logger.info("Exibindo resultado da API.")

        # Persistência do uso, se resposta válida
        if "id" in result and "usage" in result and "choices" in result:
            record = self.json_to_usage_record(result)
            self.repo.insert_usage(record)
        else:
            self.logger.warning("Resposta da API não possui campos esperados para persistência.")

        # Exibe o resultado formatado
        self.json_dumps(result)
        self.format_result_for_user(result)


if __name__ == "__main__":
    deepseek_app = LLMApiClient(prompt="Qual é a capital do Brasil?")
    deepseek_app.run()
