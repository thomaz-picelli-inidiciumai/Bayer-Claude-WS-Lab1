-- BayViva: schema do banco DuckDB (dados sintéticos).
-- Gerado e populado por db/seed.py. Não editar o banco à mão.

CREATE TABLE IF NOT EXISTS usuarios (
    id      INTEGER PRIMARY KEY,
    nome    VARCHAR NOT NULL,
    email   VARCHAR NOT NULL,          -- domínio @example.com
    papel   VARCHAR NOT NULL           -- 'representante' | 'gerente'
);

CREATE TABLE IF NOT EXISTS representantes (
    id          INTEGER PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    nome        VARCHAR NOT NULL,
    regiao      VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS medicos (
    id              INTEGER PRIMARY KEY,
    id_bayviva      VARCHAR NOT NULL UNIQUE,   -- ID interno fictício
    nome            VARCHAR NOT NULL,
    especialidade   VARCHAR NOT NULL,
    interesses      VARCHAR NOT NULL,          -- lista separada por "; "
    crm_numero      VARCHAR NOT NULL,          -- registro fictício no conselho
    crm_uf          VARCHAR NOT NULL,
    telefone        VARCHAR,                   -- faixa inexistente (DDD 00)
    email           VARCHAR,                   -- domínio @example.com
    endereco        VARCHAR,
    cidade          VARCHAR,
    estado          VARCHAR,
    pais            VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS visitas (
    id                INTEGER PRIMARY KEY,
    medico_id         INTEGER NOT NULL REFERENCES medicos(id),
    representante_id  INTEGER NOT NULL REFERENCES representantes(id),
    data_hora         TIMESTAMP NOT NULL,
    status            VARCHAR NOT NULL,        -- 'realizada' | 'planejada' | 'cancelada'
    notas             VARCHAR                  -- texto livre
);
