# crm-pharma-base (BayViva)

Repositório inicial do workshop Claude Code. CRM fictício, dados 100% sintéticos.

## Começar
```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows; Linux/Mac: .venv/bin/pip
python db/seed.py
uvicorn app.main:app --reload
```
Abra http://127.0.0.1:8000 e clique em **Entrar**.

## O que já funciona
Login, barra superior, home, contas (50 médicos de Cardiologia) com ficha.

## O que será construído nos labs
Registrar visita, painel de médicos a visitar e agenda. Specs em `docs/specs/`.

## Testes
`pytest`

## Tags de retomada
`lab0-inicio`, `lab1-pronto`, `lab2-inicio`, `lab2-solucao`, `lab3-inicio`.
