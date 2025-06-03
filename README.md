# py-ai-api-integration

Cliente Python orientado a objetos para integração e testes de APIs de IA, com foco inicial em DeepSeek, persistência de dados em SQLite e configuração flexível via YAML.

**Status:** Beta — funcional para DeepSeek, em evolução para múltiplos provedores e integração futura com Telegram.

## Funcionalidades

* Integração com API DeepSeek (outros provedores em desenvolvimento)
* Persistência de uso em SQLite
* Configuração via YAML (`src/config/settings.yaml`)
* Logging estruturado
* Tipagem completa

## Instalação

### Usando uv (recomendado)

```bash
uv venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate    # Windows
uv sync
```

### Usando pip

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate    # Windows
pip install -r requirements.txt  # ou instale manualmente as dependências
```

## Configuração

* Copie o arquivo de exemplo e edite com sua chave:

  ```bash
  cp .env.example .env
  ```

No arquivo `.env`:

  ```env
  DEEPSEEK_API_KEY=seu_token_aqui
  ```

* Ajuste parâmetros em `src/config/settings.yaml` conforme necessário.

## Uso

Execute a aplicação principal:

  ```bash
  uv run python main.py
  ```

## Estrutura do Projeto

```bash
src/
├── common/          # Utilitários comuns
├── config/          # Configurações (YAML, constantes)
├── core/            # Classes base e erros
└── repositories/    # Acesso a dados (SQLite)
```

## Roadmap

* Suporte a OpenAI, Anthropic, Google, Grok
* Integração com Telegram
* Exemplos de uso e documentação incremental

## Contato

GitHub: [pagueru](https://github.com/pagueru/)

LinkedIn: [Raphael Coelho](https://www.linkedin.com/in/raphaelhvcoelho/)

E-mail: [raphael.phael@gmail.com](mailto:raphael.phael@gmail.com)
