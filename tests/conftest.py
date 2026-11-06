import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))

import seed  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Cliente de teste com um banco sintético temporário (semente fixa)."""
    banco = tmp_path / "teste.duckdb"
    seed.criar(banco)
    monkeypatch.setenv("BAYVIVA_DB", str(banco))
    from app.main import app

    return TestClient(app)
