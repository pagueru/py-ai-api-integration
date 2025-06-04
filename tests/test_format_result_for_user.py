"""Testes unitários para o método _format_result_for_user da classe LLMApiClient."""

import pytest

from repositories.ai_repository import AiRespository
from src.core.base_class import BaseClass


class DummyEcho:
    def __init__(self):
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))


@pytest.fixture
def llm_client(monkeypatch):
    # Instancia o client e substitui echo por dummy
    client = AiRespository()
    dummy_echo = DummyEcho()
    # Corrige: monkeypatch no símbolo importado em main.py
    monkeypatch.setattr("main.echo", dummy_echo)
    return client, dummy_echo


def test_format_result_for_user_ok(llm_client):
    client, dummy_echo = llm_client
    result = {
        "choices": [{"message": {"content": "Resposta gerada."}}],
        "model": "deepseek-chat",
        "usage": {"total_tokens": 42},
        "prompt": "Pergunta de teste",
    }
    formatted = client.format_result_for_user(result)
    assert formatted == ""
    # Verifica se echo foi chamado com os textos esperados
    assert any("Resposta gerada." in call[0][0] for call in dummy_echo.calls)
    assert any("Modelo: deepseek-chat" in call[0][0] for call in dummy_echo.calls)


def test_format_result_for_user_empty(llm_client):
    client, dummy_echo = llm_client
    result = {"choices": []}
    formatted = client.format_result_for_user(result)
    assert formatted == "A resposta da API não contém os campos esperados."
    assert not dummy_echo.calls  # echo não deve ser chamado
