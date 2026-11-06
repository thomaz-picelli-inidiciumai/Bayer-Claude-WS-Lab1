# BayViva (CRM fictício para o workshop de Claude Code)

CRM simplificado para representantes da indústria farmacêutica. Tudo é fictício e sintético: nenhum dado real da Bayer entra neste repositório.

## Stack
- Python 3.11+, FastAPI, templates Jinja2 (sem build de frontend), DuckDB local.

## Comandos
- Instalar: `python -m venv .venv` e `.venv/Scripts/pip install -r requirements.txt` (Windows) ou `.venv/bin/pip ...`
- Criar o banco: `python db/seed.py` (gera `db/bayviva.duckdb`, semente fixa)
- Rodar o app: `uvicorn app.main:app --reload` e abrir http://127.0.0.1:8000
- Testes: `pytest`

## Estrutura
- `app/main.py` rotas; `app/db.py` conexão DuckDB; `app/templates/` telas; `app/static/` CSS
- `db/schema.sql` e `db/seed.py` schema e dados sintéticos
- `docs/specs/` specs: `00-visao-geral.md`, `lab1-specs/`
- `tests/` testes pytest (banco temporário por teste, via fixture `client`)

## Convenções
- Textos de interface em português do Brasil.
- Acesso a dados via `app.db.conexao()`; SQL sempre parametrizado (`?`), nunca f-string com entrada do usuário.
- DuckDB aceita um único processo de escrita: abrir conexão curta por requisição.
- Toda funcionalidade nova vem com teste. Rode `pytest` antes de commitar.
- Commits pequenos e frequentes, mensagem no imperativo.

## O que não fazer
- Não commitar `db/*.duckdb`, `.env` ou segredos.
- Não usar dados reais; e-mails em `@example.com`, telefones com DDD 00.
- Não alterar `db/seed.py` sem manter a semente fixa (todos precisam ver os mesmos números).
- Não implementar fora do escopo da spec.
