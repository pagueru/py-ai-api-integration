"""Módulo com utilitários para conversão de dicionários."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

# from src.common.logger import LoggerSingleton


@dataclass
class ResultConverter:
    """Classe utilitária para converter resultados da API em dicionários para persistência."""

    def __init__(self) -> None:
        """Inicializa a classe ResultConverter."""
        # self.logger = LoggerSingleton().logger or LoggerSingleton.get_logger()
        """Instancia o logger da aplicação."""

    def api_result_to_dict(self, result: dict[str, Any]) -> dict[str, Any]:
        """Converte o resultado da API em dicionário para uso no banco de dados."""
        try:
            usage_dict = result["usage"]
            choices_dict = result["choices"][0]
            return {
                "usage_id": result["id"],
                "object": result["object"],
                "created": result["created"],
                "model": result["model"],
                "system_fingerprint": result["system_fingerprint"],
                "prompt": result["prompt"],
                "completion": choices_dict["message"]["content"],
                "prompt_tokens": usage_dict["prompt_tokens"],
                "completion_tokens": usage_dict["completion_tokens"],
                "total_tokens": usage_dict["total_tokens"],
                "cached_tokens": usage_dict["prompt_tokens_details"]["cached_tokens"],
                "cache_hit_tokens": usage_dict["prompt_cache_hit_tokens"],
                "cache_miss_tokens": usage_dict["prompt_cache_miss_tokens"],
                "finish_reason": choices_dict["finish_reason"],
                "logprobs": choices_dict["logprobs"],
            }
        except (KeyError, IndexError, TypeError) as exc:
            msg = f"Resultado da API malformado ou incompleto: {exc}"
            raise TypeError(msg) from exc


with Path("./data/teste.json").open("r", encoding="utf-8") as file:
    data = json.load(file)
    json_data = ResultConverter().api_result_to_dict(data)
    print(json.dumps(json_data, indent=2))
