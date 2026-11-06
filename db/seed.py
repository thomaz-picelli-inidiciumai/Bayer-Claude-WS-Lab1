"""Gera o banco BayViva com dados sintéticos e semente fixa.

Uso:
    python db/seed.py                 # cria/recria db/bayviva.duckdb
    python db/seed.py --path caminho.duckdb

Todos os dados são fictícios: e-mails em @example.com, telefones com DDD 00
(faixa inexistente) e registros de conselho inventados. A semente fixa garante
que as 22 pessoas vejam exatamente os mesmos números.
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

SEED = 20261104
DATA_REFERENCIA = datetime(2026, 11, 4, 8, 0)  # data fixa; não usar "agora"
ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "db" / "schema.sql"
DEFAULT_DB = ROOT / "db" / "bayviva.duckdb"

PRIMEIROS = [
    "Ana", "Bruno", "Carla", "Diego", "Elisa", "Fábio", "Gabriela", "Hugo",
    "Iara", "João", "Karina", "Lucas", "Mariana", "Nelson", "Olívia", "Paulo",
    "Renata", "Samuel", "Tatiana", "Vinícius", "Wanda", "Yuri", "Helena", "Rafael",
]
SOBRENOMES = [
    "Almeida", "Barbosa", "Cardoso", "Dias", "Esteves", "Freitas", "Gomes",
    "Haddad", "Incerti", "Janes", "Kuhn", "Lacerda", "Monteiro", "Nogueira",
    "Oliveira", "Pacheco", "Queiroz", "Ribeiro", "Siqueira", "Teixeira",
]
INTERESSES = [
    "insuficiência cardíaca", "hipertensão resistente", "dislipidemia",
    "fibrilação atrial", "prevenção cardiovascular", "cardio-oncologia",
    "estenose aórtica", "doença coronariana estável",
]
CIDADES = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"),
    ("Porto Alegre", "RS"), ("Curitiba", "PR"), ("Salvador", "BA"),
]
REGIOES = ["Sudeste 1", "Sudeste 2", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
NOTAS = [
    "Médico pediu material sobre o protocolo de titulação; retorna em 30 dias.",
    "Demonstrou interesse em dados do estudo observacional da região.",
    "Preocupado com adesão de pacientes idosos ao tratamento.",
    "Pediu agenda de congresso para o próximo semestre.",
    "Comentou sobre concorrência de outra classe terapêutica.",
    "Visita curta, médico com agenda cheia; reagendar com antecedência.",
    "Interesse em casos de cardio-oncologia do hospital de referência.",
    "Sem interesse imediato; manter contato com envio de artigos.",
    "Relatou dificuldade de acesso a exames de controle dos pacientes.",
    "Bom receptor às informações de segurança do produto.",
]


def gerar_usuarios_representantes(rng: random.Random):
    """Seis representantes. O representante 1 é o usuário do login de demonstração."""
    usuarios = [(1, "Rep. Demonstração", "rep.demo@example.com", "representante")]
    representantes = [(1, 1, "Rep. Demonstração", REGIOES[0])]
    nomes = {"Rep. Demonstração"}
    while len(representantes) < 6:
        nome = f"{rng.choice(PRIMEIROS)} {rng.choice(SOBRENOMES)}"
        if nome in nomes:
            continue
        nomes.add(nome)
        n = len(representantes) + 1
        usuarios.append((n, nome, f"rep{n}@example.com", "representante"))
        representantes.append((n, n, nome, REGIOES[n - 1]))
    return usuarios, representantes


def gerar_medicos(rng: random.Random, quantidade: int = 50):
    medicos, nomes = [], set()
    while len(medicos) < quantidade:
        nome = f"Dr. {rng.choice(PRIMEIROS)} {rng.choice(SOBRENOMES)}"
        if nome in nomes:
            continue
        nomes.add(nome)
        n = len(medicos) + 1
        cidade, uf = rng.choice(CIDADES)
        interesses = "; ".join(rng.sample(INTERESSES, k=rng.randint(2, 3)))
        slug = nome.lower().replace("dr. ", "").replace(" ", ".")
        medicos.append((
            n,
            f"BV-{n:04d}",
            nome,
            "Cardiologia",
            interesses,
            f"{100000 + n * 37}",
            uf,
            f"+55 00 9{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}",
            f"{slug}@example.com",
            f"Rua Exemplo {rng.randint(10, 999)}, sala {rng.randint(1, 120)}",
            cidade,
            uf,
            "Brasil",
        ))
    return medicos


def gerar_visitas(rng: random.Random, n_medicos: int, n_reps: int):
    visitas = []
    vid = 1
    inicio = DATA_REFERENCIA - timedelta(days=365)
    # ~8 visitas por médico no último ano, em dias úteis, horário comercial
    for medico_id in range(1, n_medicos + 1):
        for _ in range(rng.randint(5, 11)):
            dias = rng.randint(0, 364)
            dia = inicio + timedelta(days=dias)
            if dia.weekday() >= 5:
                continue
            hora = rng.choice([8, 9, 10, 11, 14, 15, 16, 17])
            data_hora = dia.replace(hour=hora, minute=rng.choice([0, 30]))
            if data_hora >= DATA_REFERENCIA:
                continue
            status = "cancelada" if rng.random() < 0.08 else "realizada"
            notas = rng.choice(NOTAS) if status == "realizada" else None
            visitas.append((vid, medico_id, rng.randint(1, n_reps), data_hora, status, notas))
            vid += 1
    # visitas planejadas para as próximas duas semanas (alimentam a agenda)
    for medico_id in rng.sample(range(1, n_medicos + 1), k=20):
        dia = DATA_REFERENCIA + timedelta(days=rng.randint(1, 14))
        while dia.weekday() >= 5:
            dia += timedelta(days=1)
        data_hora = dia.replace(hour=rng.choice([9, 10, 14, 15]), minute=0)
        visitas.append((vid, medico_id, rng.randint(1, n_reps), data_hora, "planejada", None))
        vid += 1
    return visitas


def popular(con: duckdb.DuckDBPyConnection) -> None:
    rng = random.Random(SEED)
    usuarios, representantes = gerar_usuarios_representantes(rng)
    medicos = gerar_medicos(rng)
    visitas = gerar_visitas(rng, len(medicos), len(representantes))

    con.executemany("INSERT INTO usuarios VALUES (?, ?, ?, ?)", usuarios)
    con.executemany("INSERT INTO representantes VALUES (?, ?, ?, ?)", representantes)
    con.executemany(
        "INSERT INTO medicos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", medicos
    )
    con.executemany("INSERT INTO visitas VALUES (?, ?, ?, ?, ?, ?)", visitas)


def criar(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    con = duckdb.connect(str(path))
    try:
        con.execute(SCHEMA.read_text(encoding="utf-8"))
        popular(con)
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    criar(args.path)
    print(f"Banco criado em {args.path}")


if __name__ == "__main__":
    main()
