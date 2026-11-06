"""Testes de exemplo da base: login, home e contas."""


def test_raiz_redireciona_para_login(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"] == "/login"


def test_login_tem_botao_entrar(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert "Entrar" in r.text


def test_home_mostra_atalhos(client):
    r = client.get("/home")
    assert r.status_code == 200
    for texto in ("Registrar visita", "Registrar insight", "Nova conta"):
        assert texto in r.text


def test_contas_lista_50_medicos(client):
    r = client.get("/contas")
    assert r.status_code == 200
    assert r.text.count('href="/contas/') == 50


def test_ficha_do_medico(client):
    r = client.get("/contas/1")
    assert r.status_code == 200
    assert "BV-0001" in r.text
    assert "Cardiologia" in r.text


def test_ficha_inexistente_retorna_404(client):
    assert client.get("/contas/9999").status_code == 404


def test_seed_e_deterministico(tmp_path):
    import duckdb
    import seed

    dados = []
    for nome in ("a.duckdb", "b.duckdb"):
        p = tmp_path / nome
        seed.criar(p)
        con = duckdb.connect(str(p))
        dados.append(con.execute("SELECT count(*), sum(medico_id) FROM visitas").fetchall())
        con.close()
    assert dados[0] == dados[1]
