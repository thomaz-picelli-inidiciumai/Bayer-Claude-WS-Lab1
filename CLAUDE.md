# BayViva (CRM fictício para o workshop de Claude Code)

CRM simplificado para representantes da indústria farmacêutica. Tudo é fictício e sintético: nenhum dado real da Bayer entra neste repositório.

## Stack
- Python 3.11+, FastAPI, templates Jinja2 (sem build de frontend), DuckDB local.

## Comandos
- Instalar: `python -m venv .venv` e `.venv/Scripts/pip install -r requirements.txt` (Windows) ou `.venv/bin/pip ...`
- Criar o banco: `python db/seed.py` (gera `db/bayviva.duckdb`, semente fixa)
- Subir tudo do jeito certo: `bash iniciar.sh` (workshop, atrás do proxy) ou `bash iniciar.sh local`. Instala, cria o banco, define prefixo e porta que combinam e confere login, redirecionamento e CSS. Prefira este comando ao `uvicorn` solto: subir atrás do proxy sem `BAYVIVA_ROOT_PATH` deixa a tela sem CSS e com redirecionamentos errados.
- Rodar o app à mão: `uvicorn app.main:app --reload` e abrir http://127.0.0.1:8000
- Rodar atrás do proxy da VM (URL `https://<host-do-participante>/proxy/8000/login`): `BAYVIVA_ROOT_PATH=/proxy/8000 uvicorn app.main:app --port 8000 --proxy-headers --forwarded-allow-ips='*'`. Na porta 8001 use `/proxy/8001` e outro banco em `BAYVIVA_DB`.
- Testes: `pytest`

## Estrutura
- `app/main.py` rotas; `app/db.py` conexão DuckDB; `app/templates/` telas; `app/static/` CSS
- `db/schema.sql` e `db/seed.py` schema e dados sintéticos
- `docs/specs/` specs: `00-visao-geral.md`, `lab1-specs/`
- `tests/` testes pytest (banco temporário por teste, via fixture `client`)

## Convenções
- Links e CSS nos templates usam `{{ rota('nome_da_rota', ...) }}` (caminho com prefixo do proxy, sem host); nunca `href="/..."` fixo.
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
