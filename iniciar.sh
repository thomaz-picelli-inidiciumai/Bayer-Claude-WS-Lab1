#!/usr/bin/env bash
# Inicia o BayViva do jeito certo, sem decorar comando nenhum.
#
#   bash iniciar.sh              ambiente do workshop (atrás do proxy da VM)
#   bash iniciar.sh local        no seu computador, sem proxy
#   PORTA=8001 bash iniciar.sh   outra porta (usa outro banco e o prefixo /proxy/8001)
#   bash iniciar.sh --so-verificar   sobe, confere e encerra
#
# O que ele faz: cria o ambiente Python, instala as dependências, cria o banco se
# faltar, escolhe prefixo e porta que combinam entre si, sobe o app e CONFERE se o
# login, o redirecionamento e o CSS respondem no endereço certo.
set -euo pipefail
cd "$(dirname "$0")"

# No Git Bash (Windows) "/proxy/8000" viraria "C:/.../Git/proxy/8000". Em Linux não faz nada.
export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL='*'

MODO="vm"
SO_VERIFICAR=0
for arg in "$@"; do
  case "$arg" in
    vm|local) MODO="$arg" ;;
    --so-verificar) SO_VERIFICAR=1 ;;
    *) echo "Opção desconhecida: $arg"; echo "Use: bash iniciar.sh [vm|local] [--so-verificar]"; exit 2 ;;
  esac
done

PORTA="${PORTA:-8000}"

# 1) Python do sistema (só para criar o ambiente)
if command -v python3 >/dev/null 2>&1; then SISTEMA_PY=python3
elif command -v python >/dev/null 2>&1; then SISTEMA_PY=python
else echo "Python não encontrado. Instale o Python 3.11 ou mais novo e rode de novo."; exit 1
fi

# 2) Ambiente virtual e dependências
if [ ! -d .venv ]; then
  echo "Criando o ambiente Python (.venv)..."
  "$SISTEMA_PY" -m venv .venv
fi
if [ -x .venv/bin/python ]; then PY=.venv/bin/python
else PY=.venv/Scripts/python.exe
fi
echo "Instalando as dependências..."
"$PY" -m pip install -q --disable-pip-version-check -r requirements.txt

# 3) Banco: porta 8000 usa o banco padrão; outra porta usa o seu próprio banco
if [ "$PORTA" = "8000" ]; then
  unset BAYVIVA_DB || true
  BANCO="db/bayviva.duckdb"
else
  export BAYVIVA_DB="db/bayviva-$PORTA.duckdb"
  BANCO="$BAYVIVA_DB"
fi
if [ ! -f "$BANCO" ]; then
  echo "Criando o banco ($BANCO)..."
  if [ "$PORTA" = "8000" ]; then
    "$PY" db/seed.py
  else
    "$PY" -c "from pathlib import Path; import sys; sys.path.insert(0, 'db'); import seed; seed.criar(Path('$BANCO'))"
  fi
fi

# 4) Porta livre?
if ! "$PY" - "$PORTA" <<'PY'
import socket, sys
s = socket.socket()
try:
    s.bind(("127.0.0.1", int(sys.argv[1])))
except OSError:
    sys.exit(1)
finally:
    s.close()
PY
then
  echo "A porta $PORTA já está em uso. Provavelmente o BayViva já está rodando em outro terminal."
  echo "Feche esse terminal (Ctrl+C) ou use outra porta: PORTA=8001 bash iniciar.sh"
  exit 1
fi

# 5) Prefixo e porta combinados (é aqui que o erro do CSS nascia)
if [ "$MODO" = "vm" ]; then
  export BAYVIVA_ROOT_PATH="/proxy/$PORTA"
  PREFIXO="/proxy/$PORTA"
  EXTRA="--proxy-headers --forwarded-allow-ips=*"
else
  unset BAYVIVA_ROOT_PATH || true
  PREFIXO=""
  EXTRA=""
fi

# 6) Sobe o app
# shellcheck disable=SC2086
"$PY" -m uvicorn app.main:app --port "$PORTA" $EXTRA >/tmp/bayviva-$PORTA.log 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT INT TERM

# 7) Espera ficar de pé e confere
verificar() {
  "$PY" - "$PORTA" "$PREFIXO" <<'PY'
import http.client, re, sys
porta, prefixo = sys.argv[1], sys.argv[2]

def get(caminho):
    c = http.client.HTTPConnection("127.0.0.1", int(porta), timeout=5)
    c.request("GET", caminho)
    r = c.getresponse()
    return r.status, r.getheader("location"), r.read().decode("utf-8", "replace")

st, loc, _ = get(prefixo + "/")
assert st in (302, 307) and loc == prefixo + "/login", f"redirecionamento da raiz errado: {st} -> {loc}"
st, _, html = get(prefixo + "/login")
assert st == 200, f"a tela de login respondeu {st}"
achado = re.search(r'href="([^"]*style\.css)"', html)
assert achado, "o link do CSS não apareceu na tela"
css = achado.group(1)
assert css == prefixo + "/static/style.css", f"link do CSS errado: {css}"
st, _, _ = get(css)
assert st == 200, f"o CSS respondeu {st}"
PY
}

PRONTO=0
for _ in $(seq 1 40); do
  if verificar 2>/dev/null; then PRONTO=1; break; fi
  if ! kill -0 "$PID" 2>/dev/null; then break; fi
  sleep 0.5
done

if [ "$PRONTO" -ne 1 ]; then
  echo
  echo "O app não passou na conferência. Últimas linhas do log (/tmp/bayviva-$PORTA.log):"
  tail -n 15 "/tmp/bayviva-$PORTA.log" || true
  echo
  verificar || true
  exit 1
fi

echo
echo "BayViva no ar. Conferido: login, redirecionamento e CSS respondem."
if [ "$MODO" = "vm" ]; then
  echo "Abra no navegador:  https://<endereço do seu ambiente>${PREFIXO}/login"
  echo "(o endereço do ambiente é o mesmo que você já usa; o final tem que ser ${PREFIXO}/login)"
else
  echo "Abra no navegador:  http://127.0.0.1:${PORTA}/login"
fi
echo "Para parar: Ctrl+C."

if [ "$SO_VERIFICAR" -eq 1 ]; then exit 0; fi
wait "$PID"
