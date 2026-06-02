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

O projeto ja possui um arquivo local `.env` para execucao com Oracle. Esse arquivo esta no `.gitignore`, entao nao entra no repositiorio.

Arquivo local usado agora:

```text
HERMES_DB_TARGET=oracle
ORACLE_USER=rm551549
ORACLE_PASSWORD=090705
ORACLE_HOST=oracle.fiap.com.br
ORACLE_PORT=1521
ORACLE_SID=ORCL
```

Se quiser testar sem Oracle, troque apenas:

```text
HERMES_DB_TARGET=sqlite
```

## Como Rodar: passo a passo

### Opcao 1: rodar os scripts manualmente

1. Abra o PowerShell na pasta do projeto:

```powershell
cd C:\Users\hyeon\Desktop\GS-DATABASE\hermes-orbital-data-pipeline
```

2. Verifique se o Python funciona:

```powershell
python --version
```

Se aparecer erro de permissao no `python`, corrija isso primeiro. Neste computador isso ainda precisa ser resolvido.

3. Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Instale as dependencias:

```powershell
pip install -r requirements.txt
```

5. Execute a extracao:

```powershell
python scripts\extract_spacex.py
python scripts\extract_iss.py
python scripts\generate_mock_telemetry.py
```

6. Execute a transformacao:

```powershell
python scripts\transform_data.py
```

7. Carregue no banco:

```powershell
python scripts\load_database.py
```

8. Rode as consultas analiticas:

```powershell
python scripts\run_analytical_queries.py
```

9. Verifique as saidas:

```text
data/raw/
data/processed/
data/processed/query_results/
```

Se o Oracle falhar, o projeto deve cair para SQLite automaticamente.

### Opcao 2: rodar pelo Airflow com Docker

1. Abra o terminal na pasta do projeto:

```powershell
cd C:\Users\hyeon\Desktop\GS-DATABASE\hermes-orbital-data-pipeline
```

2. Suba a inicializacao do Airflow:

```powershell
docker compose up airflow-init
```

3. Suba os servicos:

```powershell
docker compose up
```

4. Abra o Airflow:

```text
http://localhost:8080
```

5. Entre com:

```text
usuario: admin
senha: admin
```

6. Ative a DAG `hermes_orbital_pipeline`.

7. Clique em `Trigger DAG`.

8. Acompanhe as tarefas:

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

## Ordem recomendada

Para apresentar rapido e com menos risco:

1. Tente primeiro com `HERMES_DB_TARGET=sqlite`.
2. Depois mude para `HERMES_DB_TARGET=oracle`.
3. Se Oracle responder, use ele na demonstracao.
4. Se Oracle falhar, mantenha SQLite como fallback.

## Banco Oracle

O schema Oracle esta em `sql/01_create_tables_oracle.sql`. A conexao usa `oracledb` e variaveis de ambiente.

Se quiser forcar Oracle no terminal atual sem editar arquivo:

```powershell
$env:HERMES_DB_TARGET="oracle"
$env:ORACLE_USER="rm551549"
$env:ORACLE_PASSWORD="090705"
$env:ORACLE_HOST="oracle.fiap.com.br"
$env:ORACLE_PORT="1521"
$env:ORACLE_SID="ORCL"
python scripts\load_database.py
```

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
