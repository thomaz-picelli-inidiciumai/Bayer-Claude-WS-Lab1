"""Acesso ao DuckDB do BayViva.

O DuckDB aceita um único processo de escrita; abrimos uma conexão curta por
requisição. Em testes, aponte BAYVIVA_DB para um banco temporário.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent


def db_path() -> Path:
    return Path(os.environ.get("BAYVIVA_DB", ROOT / "db" / "bayviva.duckdb"))


@contextmanager
def conexao(somente_leitura: bool = False):
    con = duckdb.connect(str(db_path()), read_only=somente_leitura)
    try:
        yield con
    finally:
        con.close()
