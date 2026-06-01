# Hermes Orbital Data Pipeline

Projeto de pipeline de dados para a Global Solution 2026 da FIAP.

## Integrantes

Preencha aqui os nomes, RMs e turma dos integrantes.

## Objetivo

O Projeto Hermes simula uma solucao da industria espacial para monitoramento orbital, remocao de lixo espacial, extensao da vida util de satelites, taxiamento orbital e reabastecimento de modulos em orbita.

O pipeline extrai dados externos, gera telemetria orbital mockada, transforma os dados com Pandas, carrega em Oracle ou SQLite e executa consultas analiticas SQL.

## Fontes de Dados

- SpaceX API: `https://api.spacexdata.com/v4/launches`
- Open Notify API: `http://api.open-notify.org/iss-now.json`
- Dados mockados Hermes: `data/raw/hermes_orbital_telemetry.csv` e `data/mock/hermes_orbital_telemetry.csv`

Se uma API externa falhar, os extratores usam fallback local em `data/mock`.

## Arquitetura

```text
Extracao -> Raw Files -> Transformacao Pandas -> Oracle/SQLite -> Consultas SQL
```

A DAG Airflow esta em `dags/hermes_orbital_pipeline_dag.py` e contem as tarefas:

```text
create_directories
extract_spacex_launches
extract_iss_position
generate_mock_telemetry
transform_spacex_data
transform_iss_data
transform_telemetry_data
load_to_database
run_analytical_queries
```

## Configuracao

Copie `.env.example` para `.env` se quiser alterar as variaveis locais.

Variaveis principais:

```text
HERMES_DB_TARGET=sqlite
ORACLE_USER=
ORACLE_PASSWORD=
ORACLE_HOST=oracle.fiap.com.br
ORACLE_PORT=1521
ORACLE_SID=ORCL
```

Use `HERMES_DB_TARGET=oracle` apenas quando as credenciais Oracle estiverem disponiveis. Caso a conexao Oracle falhe, o loader usa SQLite como fallback.

## Rodando Manualmente

No diretorio do projeto:

```bash
cd hermes-orbital-data-pipeline
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/extract_spacex.py
python scripts/extract_iss.py
python scripts/generate_mock_telemetry.py
python scripts/transform_data.py
python scripts/load_database.py
python scripts/run_analytical_queries.py
```

O banco SQLite sera criado em:

```text
hermes_orbital.db
```

Os resultados das consultas ficam em:

```text
data/processed/query_results/
```

## Rodando com Docker Compose

No diretorio do projeto:

```bash
docker compose up airflow-init
docker compose up
```

Acesse o Airflow em:

```text
http://localhost:8080
```

Credenciais padrao:

```text
usuario: admin
senha: admin
```

Ative e execute a DAG `hermes_orbital_pipeline`.

## Banco Oracle

O schema Oracle esta em `sql/01_create_tables_oracle.sql`. A conexao usa `python-oracledb` e variaveis de ambiente, sem senha fixa no codigo.

## Banco SQLite

O schema SQLite esta em `sql/02_create_tables_sqlite.sql`. Ele e o modo recomendado para testes locais e apresentacao quando o Oracle externo nao estiver acessivel.

## Consultas Analiticas

As consultas obrigatorias e opcionais estao em:

- `sql/03_analytical_queries_oracle.sql`
- `sql/04_analytical_queries_sqlite.sql`

Consultas incluidas:

1. Quantidade de objetos orbitais por tipo.
2. Media, minimo e maximo do risco de colisao por zona orbital.
3. Ranking dos 10 objetos com maior risco de colisao.
4. Quantidade de missoes recomendadas por tipo de acao.
5. Consumo total de combustivel estimado por nivel de prioridade.
6. Lancamentos SpaceX bem-sucedidos e malsucedidos por ano.
7. Ultimas posicoes registradas da ISS.

## Prints Esperados para Documentacao

- Tela da DAG no Airflow com todas as tarefas.
- Execucao bem-sucedida da DAG.
- Arquivos em `data/raw` e `data/processed`.
- Tabelas criadas no SQLite ou Oracle.
- Resultados CSV em `data/processed/query_results`.
- Saida de uma consulta analitica demonstrando risco orbital e recomendacoes.
