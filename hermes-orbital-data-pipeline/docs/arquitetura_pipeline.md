# Arquitetura do Pipeline Hermes

O Projeto Hermes usa um pipeline em camadas para coletar, transformar, persistir e consultar dados relacionados a operacoes orbitais.

## Camadas

1. Extracao: scripts em `scripts/extract_*.py` consomem SpaceX API e Open Notify API com timeout e fallback local.
2. Dados mockados: `generate_mock_telemetry.py` simula objetos orbitais com riscos coerentes para remocao de lixo espacial, taxiamento orbital e reabastecimento.
3. Staging: arquivos brutos sao salvos em `data/raw`.
4. Transformacao: `transform_data.py` valida arquivos, remove registros invalidos, padroniza datas, converte tipos numericos e cria regras de prioridade.
5. Persistencia: `load_database.py` direciona a carga para Oracle ou SQLite.
6. Analytics: `run_analytical_queries.py` executa as consultas SQLite e salva resultados em `data/processed/query_results`.

## Orquestracao Airflow

A DAG `hermes_orbital_pipeline` executa o seguinte fluxo:

```text
create_directories >> [extract_spacex_launches, extract_iss_position, generate_mock_telemetry]
extract_spacex_launches >> transform_spacex_data
extract_iss_position >> transform_iss_data
generate_mock_telemetry >> transform_telemetry_data
[transform_spacex_data, transform_iss_data, transform_telemetry_data] >> load_to_database >> run_analytical_queries
```

## Banco de Dados

O alvo padrao e SQLite local, criado em `hermes_orbital.db`. Para Oracle, defina `HERMES_DB_TARGET=oracle` e as variaveis `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_HOST`, `ORACLE_PORT` e `ORACLE_SID`.
