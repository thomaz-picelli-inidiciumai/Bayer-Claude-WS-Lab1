# crm-pharma-base (BayViva)

Repositório inicial do workshop Claude Code. CRM fictício, dados 100% sintéticos.

## Começar (um comando só)
No ambiente do workshop (atrás do proxy da VM):
```bash
bash iniciar.sh
```
No seu computador, sem proxy: `bash iniciar.sh local`.

O script cria o ambiente Python, instala as dependências, cria o banco, sobe o app com o
prefixo e a porta certos e **confere** se o login, o redirecionamento e o CSS respondem. Ele
termina mostrando o endereço para abrir (`.../proxy/8000/login`). Se algo estiver errado, ele
diz o que, em vez de subir uma tela sem CSS. Outra porta: `PORTA=8001 bash iniciar.sh`.

### Passo a passo manual (só se precisar)
```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows; Linux/Mac: .venv/bin/pip
python db/seed.py
uvicorn app.main:app --reload
```
Abra http://127.0.0.1:8000 e clique em **Entrar**.

Atrás do proxy da VM (`https://<seu-host>/proxy/8000/login`):
```bash
BAYVIVA_ROOT_PATH=/proxy/8000 uvicorn app.main:app --port 8000 --proxy-headers --forwarded-allow-ips='*'
```

## O que já funciona
Login, barra superior, home, contas (50 médicos de Cardiologia) com ficha.

## O que será construído nos labs
Registrar visita, painel de médicos a visitar e agenda. Specs em `docs/specs/`.

## Testes
`pytest`

## Tags de retomada
`lab0-inicio`, `lab1-pronto`, `lab2-inicio`, `lab2-solucao`, `lab3-inicio`.
