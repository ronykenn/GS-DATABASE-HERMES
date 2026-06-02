# Hermes Orbital Data Pipeline

## Integrantes

- Nome completo: `PREENCHER`
- RM: `PREENCHER`
- Nome completo: `PREENCHER`
- RM: `PREENCHER`

## Descricao da Solucao Proposta

O Projeto Hermes apresenta uma pipeline de dados para o contexto da industria espacial, com foco em monitoramento orbital, remocao de lixo espacial, extensao da vida util de satelites, taxiamento orbital e reabastecimento de modulos em orbita.

A solucao integra dados reais de APIs externas com dados simulados de telemetria orbital. O pipeline executa extracao, transformacao, carga em banco Oracle e consultas analiticas SQL, com fallback em SQLite para testes locais.

## Objetivo do Pipeline

O objetivo do pipeline e automatizar o fluxo completo de dados do Projeto Hermes:

- coletar dados externos relacionados a operacoes espaciais;
- gerar telemetria orbital coerente com o problema de negocio;
- tratar e padronizar os dados;
- carregar os dados em Oracle Database;
- gerar analises para apoio a decisao operacional.

## Fontes de Dados Utilizadas

### 1. SpaceX API

- Base URL: `https://api.spacexdata.com/v4`
- Endpoint utilizado: `https://api.spacexdata.com/v4/launches`
- Finalidade: coletar historico de lancamentos, sucesso das missoes, foguetes, bases de lancamento e detalhes das operacoes.

### 2. Open Notify API

- Endpoint utilizado: `http://api.open-notify.org/iss-now.json`
- Finalidade: coletar a posicao atual da ISS.

### 3. Dados mockados do Projeto Hermes

- Arquivo gerado: `data/raw/hermes_orbital_telemetry.csv`
- Finalidade: simular objetos orbitais com altitude, velocidade, massa, risco de colisao, status operacional, combustivel estimado e acao recomendada.

## Arquitetura do Pipeline

Fluxo visual do pipeline:

```text
fonte de dados -> extracao -> transformacao -> carga no Oracle -> analise SQL
```

Fluxo detalhado:

```text
SpaceX API -------------------\
                               -> data/raw -> transformacoes -> data/processed -> Oracle Database -> consultas SQL
Open Notify API -------------/
Mock telemetry Hermes -------/
```

## Estrutura do Projeto

```text
hermes-orbital-data-pipeline/
|-- dags/
|   |-- hermes_orbital_pipeline_dag.py
|-- scripts/
|   |-- extract_spacex.py
|   |-- extract_iss.py
|   |-- generate_mock_telemetry.py
|   |-- transform_data.py
|   |-- load_oracle.py
|   |-- load_sqlite.py
|   |-- load_database.py
|   |-- run_analytical_queries.py
|-- sql/
|   |-- 01_create_tables_oracle.sql
|   |-- 02_create_tables_sqlite.sql
|   |-- 03_analytical_queries_oracle.sql
|   |-- 04_analytical_queries_sqlite.sql
|-- data/
|   |-- raw/
|   |-- processed/
|   |-- mock/
|-- docs/
```

## Explicacao das Etapas da DAG

A DAG `hermes_orbital_pipeline` foi criada em [hermes_orbital_pipeline_dag.py](/c:/Users/hyeon/Desktop/GS-DATABASE/hermes-orbital-data-pipeline/dags/hermes_orbital_pipeline_dag.py).

As tarefas sao:

1. `create_directories`
Cria a estrutura inicial de pastas do projeto.

2. `extract_spacex_launches`
Extrai os dados da API da SpaceX com timeout e fallback local.

3. `extract_iss_position`
Extrai a posicao da ISS com timeout e fallback local.

4. `generate_mock_telemetry`
Gera a base simulada de objetos orbitais do Projeto Hermes.

5. `transform_spacex_data`
Trata os dados da SpaceX.

6. `transform_iss_data`
Trata os dados da ISS.

7. `transform_telemetry_data`
Trata a telemetria orbital mockada.

8. `load_to_database`
Realiza a carga no Oracle Database. Se houver falha, existe fallback para SQLite.

9. `run_analytical_queries`
Executa as consultas analiticas e exporta os resultados em CSV.

Dependencias da DAG:

```text
create_directories >> [extract_spacex_launches, extract_iss_position, generate_mock_telemetry]
extract_spacex_launches >> transform_spacex_data
extract_iss_position >> transform_iss_data
generate_mock_telemetry >> transform_telemetry_data
[transform_spacex_data, transform_iss_data, transform_telemetry_data] >> load_to_database >> run_analytical_queries
```

## Transformacoes Realizadas

As transformacoes implementadas em [transform_data.py](/c:/Users/hyeon/Desktop/GS-DATABASE/hermes-orbital-data-pipeline/scripts/transform_data.py) foram:

- remocao de registros invalidos;
- padronizacao de datas para timestamp;
- conversao de latitude, longitude, altitude, velocidade, massa, risco e combustivel para tipos numericos;
- tratamento de valores nulos;
- remocao de duplicidades;
- criacao da coluna `priority_level`;
- criacao da coluna `recommended_action`;
- geracao da tabela agregada `HERMES_MISSION_ANALYTICS`.

Regras de classificacao:

- `CRITICAL`: risco maior ou igual a 80
- `HIGH`: risco maior ou igual a 60
- `MEDIUM`: risco maior ou igual a 40
- `LOW`: risco abaixo de 40

Regras de acao:

- `CRITICAL` -> `IMMEDIATE_DEORBIT`
- `HIGH` -> `SCHEDULE_CAPTURE`
- `MEDIUM` -> `MONITOR` ou `ORBITAL_TAXI` para satelites ativos
- `LOW` -> `NO_ACTION`

## Modelagem das Tabelas no Oracle

### HERMES_SPACEX_LAUNCHES

- `launch_id` VARCHAR2(100) PRIMARY KEY
- `mission_name` VARCHAR2(255)
- `flight_number` NUMBER
- `launch_date_utc` TIMESTAMP
- `success` NUMBER(1)
- `rocket_id` VARCHAR2(100)
- `launchpad_id` VARCHAR2(100)
- `payloads_count` NUMBER
- `details` VARCHAR2(1000)
- `data_source` VARCHAR2(50)
- `ingestion_date` TIMESTAMP

### HERMES_ISS_POSITION

- `position_id` VARCHAR2(100) PRIMARY KEY
- `latitude` NUMBER(10,6)
- `longitude` NUMBER(10,6)
- `timestamp_unix` NUMBER
- `collected_at` TIMESTAMP
- `data_source` VARCHAR2(50)
- `ingestion_date` TIMESTAMP

### HERMES_ORBITAL_OBJECTS

- `object_id` VARCHAR2(100) PRIMARY KEY
- `object_name` VARCHAR2(255)
- `object_type` VARCHAR2(50)
- `orbit_zone` VARCHAR2(50)
- `altitude_km` NUMBER(10,2)
- `velocity_kmh` NUMBER(10,2)
- `estimated_mass_kg` NUMBER(10,2)
- `collision_risk_score` NUMBER(5,2)
- `operational_status` VARCHAR2(50)
- `priority_level` VARCHAR2(20)
- `recommended_action` VARCHAR2(100)
- `fuel_required_kg` NUMBER(10,2)
- `observed_at` TIMESTAMP
- `data_source` VARCHAR2(50)
- `ingestion_date` TIMESTAMP

### HERMES_MISSION_ANALYTICS

- `analytic_id` VARCHAR2(100) PRIMARY KEY
- `reference_date` DATE
- `total_objects` NUMBER
- `high_risk_objects` NUMBER
- `avg_collision_risk` NUMBER(5,2)
- `total_fuel_required_kg` NUMBER(10,2)
- `generated_at` TIMESTAMP

## Evidencias de Execucao

### Execucao manual do pipeline

Fluxo executado com sucesso:

```powershell
python scripts\extract_spacex.py
python scripts\extract_iss.py
python scripts\generate_mock_telemetry.py
python scripts\transform_data.py
python scripts\load_database.py
python scripts\run_analytical_queries.py
```

Resultados confirmados:

- `205` registros carregados em `HERMES_SPACEX_LAUNCHES`
- `1` registro carregado em `HERMES_ISS_POSITION`
- `120` registros carregados em `HERMES_ORBITAL_OBJECTS`
- `1` registro carregado em `HERMES_MISSION_ANALYTICS`

### Prints obrigatorios para inserir no PDF

Inserir os seguintes prints:

1. tela do Airflow com a DAG `hermes_orbital_pipeline`;
2. graph view da DAG com dependencias;
3. execucao bem-sucedida das tarefas;
4. terminal com `Carga Oracle finalizada`;
5. tabelas do Oracle populadas;
6. resultados das consultas analiticas.

## Consultas Analiticas SQL

As consultas foram implementadas em:

- [03_analytical_queries_oracle.sql](/c:/Users/hyeon/Desktop/GS-DATABASE/hermes-orbital-data-pipeline/sql/03_analytical_queries_oracle.sql)
- [04_analytical_queries_sqlite.sql](/c:/Users/hyeon/Desktop/GS-DATABASE/hermes-orbital-data-pipeline/sql/04_analytical_queries_sqlite.sql)

### Consulta 1

Quantidade de objetos orbitais por tipo.

### Consulta 2

Media, minimo e maximo do risco de colisao por zona orbital.

### Consulta 3

Ranking dos 10 objetos com maior risco de colisao.

### Consulta 4

Quantidade de missoes recomendadas por tipo de acao.

### Consulta 5

Consumo total de combustivel estimado por nivel de prioridade.

### Consulta 6

Comparacao entre lancamentos SpaceX bem-sucedidos e malsucedidos por ano.

### Consulta 7

Ultimas posicoes registradas da ISS.

## Resultados Obtidos Pelas Consultas

Os resultados das consultas foram exportados para:

- `data/processed/query_results/oracle_query_01.csv` a `oracle_query_07.csv`
- `data/processed/query_results/sqlite_query_01.csv` a `sqlite_query_07.csv`

Sugestao para o PDF:

- inserir print de pelo menos 5 CSVs abertos;
- destacar o ranking de risco, o total por tipo de objeto e o consumo de combustivel por prioridade.

## Conclusao Tecnica da Equipe

O pipeline desenvolvido atende ao ciclo completo de engenharia de dados exigido na disciplina: extracao, integracao, transformacao, carga no Oracle Database, orquestracao por Airflow e analise SQL.

Do ponto de vista tecnico, a solucao apresenta:

- integracao com fontes externas reais;
- resiliencia com fallback local;
- tratamento de dados estruturado com Pandas;
- modelagem relacional adequada ao problema;
- carga validada no Oracle;
- consultas analiticas relevantes para tomada de decisao no contexto orbital.

A proposta e consistente com o objetivo do Projeto Hermes e demonstra um fluxo claro desde a origem dos dados ate o consumo analitico.

## Checklist Final da Entrega

- [ ] preencher nomes completos e RMs dos integrantes
- [ ] inserir prints do Airflow
- [ ] inserir prints do Oracle
- [ ] inserir prints dos resultados das consultas
- [ ] exportar este arquivo para PDF unico
- [ ] compactar o projeto em `.zip`
