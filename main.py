"""Módulo principal da aplicação."""

from dotenv import load_dotenv

from src.repositories.ai_repository import AiRespository

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

if __name__ == "__main__":
    deepseek_app = AiRespository()
    deepseek_app.run(prompt="Qual a capital do Brasil?")
