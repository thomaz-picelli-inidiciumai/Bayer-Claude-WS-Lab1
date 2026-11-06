# BayViva: visão geral

CRM fictício para representantes de uma indústria farmacêutica visitarem médicos. Todos os dados são sintéticos.

## Usuário
Representante de vendas (usuário de demonstração: Rep. Demonstração, representante 1).

## Telas
| Tela | Estado na base |
| --- | --- |
| Login, barra superior, home, contas e ficha do médico | Prontas |
| Registrar visita | A construir (Labs 1 e 2) |
| Painel de médicos a visitar | A construir |
| Agenda de visitas | A construir |
| Registrar insight, Nova conta | Botões sem funcionalidade (extensão) |

## Dados (DuckDB, `db/schema.sql`)
`usuarios`, `representantes`, `medicos` (ficha completa), `visitas` (status: realizada, planejada, cancelada).
