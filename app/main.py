"""BayViva: CRM fictício para representantes da indústria farmacêutica.

Estado da base: login, home e contas (médicos) prontos.
Registrar visita, painel e agenda são construídos nos Labs 1 e 2.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import conexao

BASE = Path(__file__).resolve().parent
app = FastAPI(title="BayViva")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

# Login sem senha: o botão Entrar leva ao usuário de demonstração.
USUARIO_DEMO = {"nome": "Rep. Demonstração", "iniciais": "RD"}


def contexto(request: Request, **extra):
    return {"request": request, "usuario": USUARIO_DEMO, **extra}


@app.get("/")
def raiz():
    return RedirectResponse("/login")


@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@app.get("/home")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", contexto(request, ativo="home"))


@app.get("/contas")
def contas(request: Request, q: str = ""):
    sql = "SELECT id, nome, especialidade, cidade, estado FROM medicos"
    params: list = []
    if q.strip():
        sql += " WHERE lower(nome) LIKE ?"
        params.append(f"%{q.strip().lower()}%")
    sql += " ORDER BY id"
    with conexao(somente_leitura=True) as con:
        medicos = con.execute(sql, params).fetchall()
    return templates.TemplateResponse(
        request, "contas.html", contexto(request, ativo="contas", medicos=medicos, q=q)
    )


@app.get("/contas/{medico_id}")
def ficha(request: Request, medico_id: int):
    with conexao(somente_leitura=True) as con:
        cur = con.execute("SELECT * FROM medicos WHERE id = ?", [medico_id])
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Médico não encontrado")
        medico = dict(zip([d[0] for d in cur.description], row))
    medico["interesses"] = medico["interesses"].split("; ")
    return templates.TemplateResponse(
        request, "ficha.html", contexto(request, ativo="contas", m=medico)
    )


@app.get("/em-construcao/{nome}")
def em_construcao(request: Request, nome: str):
    """Destino dos itens de menu e atalhos ainda não implementados."""
    return templates.TemplateResponse(
        request, "em_construcao.html", contexto(request, ativo=nome, nome=nome)
    )
