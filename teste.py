import json
from typing import Any


def flatten_dict(d: dict[str, Any], parent_key: str = "", sep: str = "_") -> dict[str, Any]:
    """Flatten arbitrarily nested dictionaries."""
    items: dict[str, Any] = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            # Se for lista, processa cada item
            for idx, item in enumerate(v):
                if isinstance(item, dict):
                    items.update(flatten_dict(item, f"{new_key}{sep}{idx}", sep=sep))
                else:
                    items[f"{new_key}{sep}{idx}"] = item
        else:
            items[new_key] = v
    return items


data = {
    "id": "8ecb4098-d4d8-4e6f-8e15-40fc49fa4409",
    "object": "chat.completion",
    "created": 1748990439,
    "model": "deepseek-chat",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "Brasília."},
            "logprobs": None,
            "finish_reason": "stop",
        }
    ],
    "usage": {
        "prompt_tokens": 24,
        "completion_tokens": 4,
        "total_tokens": 28,
        "prompt_tokens_details": {"cached_tokens": 0},
        "prompt_cache_hit_tokens": 0,
        "prompt_cache_miss_tokens": 24,
    },
    "system_fingerprint": "fp_8802369eaa_prod0425fp8",
    "prompt": "Explique IA em uma frase.",
}

flattened = flatten_dict(data)

print(json.dumps(flattened, indent=2))
