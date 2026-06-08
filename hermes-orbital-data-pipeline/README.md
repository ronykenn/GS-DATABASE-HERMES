# Hermes Orbital Data Pipeline

Pipeline de dados desenvolvido para a **Global Solution 2026 FIAP** no contexto do **Projeto Hermes**, uma solução conectada à Indústria Espacial para monitoramento orbital, classificação de risco de detritos, apoio à remoção de lixo espacial, extensão da vida útil de satélites, taxiamento orbital e reabastecimento de módulos em órbita.

## Integrantes

| Nome | RM |
|---|---|
| Aksel Viktor Caminha Rae | 99011 |
| Ian Xavier Kuraoka | 98860 |
| Lucas Laia Manentti | 97709 |
| Rony Ken Nagai | 551549 |
| Tomáz Versolato Carballo | 551417 |

## Objetivo do pipeline

Automatizar um fluxo completo de engenharia de dados usando **Apache Airflow**:

1. extrair dados espaciais de APIs públicas;
2. gerar telemetria orbital simulada do Projeto Hermes;
3. armazenar dados brutos em arquivos locais;
4. transformar, limpar e padronizar os dados;
5. carregar os dados em Oracle ou SQLite;
6. executar consultas analíticas SQL.

Fluxo geral:

```text
Fonte de dados -> Extração -> Raw files -> Transformação Pandas -> Banco de dados -> Consultas SQL -> Resultados analíticos
```

## Fontes de dados

| Fonte | Tipo | Uso |
|---|---|---|
| SpaceX API | API pública | Dados reais de lançamentos espaciais |
| Open Notify API | API pública | Localização atual da ISS |
| Mock Hermes Telemetry | CSV/JSON simulado | Objetos orbitais, detritos, risco de colisão, combustível e ação recomendada |

Endpoints:

```text
https://api.spacexdata.com/v4/launches
http://api.open-notify.org/iss-now.json
```

Se uma API falhar, os scripts usam fallback local em `data/mock`, evitando que a apresentação trave.

## Estrutura do projeto

```text
hermes-orbital-data-pipeline/
├── dags/
│   └── hermes_orbital_pipeline_dag.py
├── scripts/
│   ├── config.py
│   ├── extract_spacex.py
│   ├── extract_iss.py
│   ├── generate_mock_telemetry.py
│   ├── transform_data.py
│   ├── load_database.py
│   ├── load_oracle.py
│   ├── load_sqlite.py
│   └── run_analytical_queries.py
├── sql/
│   ├── 01_create_tables_oracle.sql
│   ├── 02_create_tables_sqlite.sql
│   ├── 03_analytical_queries_oracle.sql
│   └── 04_analytical_queries_sqlite.sql
├── data/
│   ├── raw/
│   ├── mock/
│   └── processed/
├── docs/
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## DAG do Airflow

Arquivo:

```text
dags/hermes_orbital_pipeline_dag.py
```

Nome da DAG:

```text
hermes_orbital_pipeline
```

Tarefas:

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

Dependências:

```text
create_directories
        |
        +--> extract_spacex_launches --> transform_spacex_data
        +--> extract_iss_position -----> transform_iss_data
        +--> generate_mock_telemetry --> transform_telemetry_data

[transform_spacex_data, transform_iss_data, transform_telemetry_data]
        |
        v
load_to_database
        |
        v
run_analytical_queries
```

## Transformações realizadas

O pipeline realiza:

1. criação automática das pastas de dados;
2. extração de dados brutos para `data/raw`;
3. geração de dados mockados de telemetria orbital;
4. remoção de registros inválidos;
5. remoção de duplicidades;
6. tratamento de valores nulos;
7. conversão de tipos numéricos;
8. padronização de datas;
9. seleção de colunas relevantes;
10. criação de `priority_level` e `recommended_action`.

Regras de prioridade:

| collision_risk_score | priority_level |
|---|---|
| >= 80 | CRITICAL |
| >= 60 e < 80 | HIGH |
| >= 40 e < 60 | MEDIUM |
| < 40 | LOW |

Regras de ação:

| priority_level | recommended_action |
|---|---|
| CRITICAL | IMMEDIATE_DEORBIT |
| HIGH | SCHEDULE_CAPTURE |
| MEDIUM | MONITOR |
| LOW | NO_ACTION |

## Modelagem das tabelas

Scripts:

```text
sql/01_create_tables_oracle.sql
sql/02_create_tables_sqlite.sql
```

Tabelas:

| Tabela | Finalidade |
|---|---|
| HERMES_SPACEX_LAUNCHES | Lançamentos extraídos da SpaceX API |
| HERMES_ISS_POSITION | Posições coletadas da ISS |
| HERMES_ORBITAL_OBJECTS | Telemetria simulada de objetos orbitais |
| HERMES_MISSION_ANALYTICS | Agregações analíticas da missão |

## Pré-requisitos

- Git;
- Python 3.10 ou superior;
- Docker Desktop;
- PowerShell ou terminal equivalente;
- acesso à internet para APIs externas;
- acesso ao Oracle FIAP, caso a equipe use Oracle.

O modo mais seguro para teste e apresentação é SQLite local. O Oracle pode ser usado quando a conexão da FIAP estiver funcionando.

## Configuração inicial

Entrar na pasta do projeto:

```powershell
cd C:\Users\hyeon\Desktop\GS-DATABASE\hermes-orbital-data-pipeline
```

Ou clonar do zero:

```powershell
git clone https://github.com/ronykenn/GS-DATABASE-HERMES.git
cd GS-DATABASE-HERMES\hermes-orbital-data-pipeline
```

Criar o `.env` local:

```powershell
copy .env.example .env
```

Configuração recomendada para SQLite:

```text
AIRFLOW_UID=50000
HERMES_DB_TARGET=sqlite
ORACLE_USER=
ORACLE_PASSWORD=
ORACLE_HOST=oracle.fiap.com.br
ORACLE_PORT=1521
ORACLE_SID=ORCL
```

Para Oracle, preencher `ORACLE_USER` e `ORACLE_PASSWORD` no arquivo `.env` local e trocar:

```text
HERMES_DB_TARGET=oracle
```

Importante: o arquivo `.env` não deve ser enviado ao GitHub.

## Rodar manualmente sem Airflow

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\extract_spacex.py
python scripts\extract_iss.py
python scripts\generate_mock_telemetry.py
python scripts\transform_data.py
python scripts\load_database.py
python scripts\run_analytical_queries.py
```

Verificar saídas:

```powershell
dir data\raw
dir data\processed
dir data\processed\query_results
```

## Rodar com Airflow e Docker

Este é o modo principal da entrega.

1. Entrar na pasta:

```powershell
cd C:\Users\hyeon\Desktop\GS-DATABASE\hermes-orbital-data-pipeline
```

2. Criar `.env`:

```powershell
copy .env.example .env
```

3. Subir inicialização do Airflow:

```powershell
docker compose up airflow-init
```

4. Subir webserver e scheduler:

```powershell
docker compose up
```

5. Acessar:

```text
http://localhost:8080
```

Login local padrão criado pelo Docker Compose:

```text
usuário: admin
senha: admin
```

6. No Airflow:

- procurar a DAG `hermes_orbital_pipeline`;
- ativar a DAG;
- clicar em `Trigger DAG`;
- acompanhar pela `Grid View`, `Graph View` e logs.

7. Ao finalizar, parar os containers:

```powershell
docker compose down
```

Para apagar o volume do Postgres do Airflow e reiniciar do zero:

```powershell
docker compose down -v
```

## Rodar com Oracle FIAP

Banco da disciplina:

```text
Host: oracle.fiap.com.br
Porta: 1521
SID: ORCL
```

No `.env` local:

```text
HERMES_DB_TARGET=oracle
ORACLE_USER=seu_usuario_fiap
ORACLE_PASSWORD=sua_senha_fiap
ORACLE_HOST=oracle.fiap.com.br
ORACLE_PORT=1521
ORACLE_SID=ORCL
```

Depois rode pelo Airflow ou manualmente.

Se o Oracle falhar por rede, acesso, credenciais ou instabilidade, o script `load_database.py` usa SQLite como fallback.

## Consultas analíticas SQL

Arquivos:

```text
sql/03_analytical_queries_oracle.sql
sql/04_analytical_queries_sqlite.sql
```

Consultas incluídas:

1. quantidade de objetos orbitais por tipo;
2. média, mínimo e máximo do risco de colisão por zona orbital;
3. ranking dos 10 objetos com maior risco de colisão;
4. quantidade de missões recomendadas por tipo de ação;
5. consumo total de combustível estimado por nível de prioridade;
6. lançamentos SpaceX bem-sucedidos e malsucedidos por ano;
7. últimas posições registradas da ISS.

## Onde tirar prints para a entrega

Use estes prints no PDF final:

1. **Estrutura do projeto no VS Code** mostrando `dags`, `scripts`, `sql`, `data`, `docs`, `docker-compose.yml` e `README.md`.
2. **Arquivo da DAG** aberto em `dags/hermes_orbital_pipeline_dag.py`, mostrando nome da DAG e tarefas.
3. **Terminal com Docker** após executar `docker compose up`, mostrando webserver e scheduler rodando.
4. **Tela inicial do Airflow** em `http://localhost:8080`, mostrando a DAG `hermes_orbital_pipeline`.
5. **DAG ativada** no Airflow com o toggle ligado.
6. **Graph View da DAG**, mostrando o fluxo completo das tarefas.
7. **Grid View ou Graph View com sucesso**, mostrando todas as tarefas verdes após `Trigger DAG`.
8. **Logs de `extract_spacex_launches` ou `extract_iss_position`**, provando extração externa.
9. **Logs de `generate_mock_telemetry`**, provando geração dos dados simulados Hermes.
10. **Logs de `transform_telemetry_data`**, provando tratamento dos dados.
11. **Logs de `load_to_database`**, provando carga em Oracle ou SQLite.
12. **Logs de `run_analytical_queries`**, provando execução das consultas.
13. **Pasta `data/raw`**, mostrando arquivos brutos gerados.
14. **Pasta `data/processed`**, mostrando arquivos tratados.
15. **Pasta `data/processed/query_results`**, mostrando resultados das consultas.
16. **Banco populado**, com contagem das tabelas em Oracle, SQLite, DBeaver, SQL Developer ou DB Browser.
17. **Consulta analítica de agrupamento**, por exemplo objetos por tipo.
18. **Ranking de risco orbital**, mostrando os objetos com maior `collision_risk_score`.

Consultas boas para prints:

```sql
SELECT object_type, COUNT(*) AS total_objects
FROM HERMES_ORBITAL_OBJECTS
GROUP BY object_type
ORDER BY total_objects DESC;
```

Oracle:

```sql
SELECT object_id, object_name, object_type, orbit_zone, collision_risk_score, priority_level, recommended_action
FROM HERMES_ORBITAL_OBJECTS
ORDER BY collision_risk_score DESC
FETCH FIRST 10 ROWS ONLY;
```

SQLite:

```sql
SELECT object_id, object_name, object_type, orbit_zone, collision_risk_score, priority_level, recommended_action
FROM HERMES_ORBITAL_OBJECTS
ORDER BY collision_risk_score DESC
LIMIT 10;
```

## Checklist do PDF final

O PDF único deve conter:

- nomes e RMs dos integrantes;
- descrição da solução proposta;
- objetivo do pipeline;
- descrição das fontes de dados;
- arquitetura do pipeline;
- explicação das etapas da DAG;
- descrição das transformações realizadas;
- modelagem das tabelas;
- prints da execução no Apache Airflow;
- prints das tabelas populadas no Oracle ou SQLite;
- no mínimo 5 consultas analíticas SQL;
- resultados das consultas;
- conclusão técnica da equipe.

## Checklist do ZIP complementar

Enviar compactado:

```text
dags/
scripts/
sql/
data/mock/
docs/
README.md
requirements.txt
docker-compose.yml
.env.example
```

Não enviar:

```text
.env
.venv/
__pycache__/
*.db
data/processed/
```

## Ordem recomendada para apresentação

1. rodar primeiro com `HERMES_DB_TARGET=sqlite`;
2. confirmar que a DAG executa inteira;
3. tirar os prints do Airflow;
4. testar Oracle depois;
5. usar Oracle na documentação se funcionar;
6. se Oracle falhar, usar SQLite como estrutura alternativa de armazenamento, conforme permitido no enunciado.

## Problemas comuns

### A DAG não aparece

Verifique se o arquivo está em:

```text
dags/hermes_orbital_pipeline_dag.py
```

Reinicie:

```powershell
docker compose down
docker compose up
```

### Porta 8080 ocupada

Altere no `docker-compose.yml`:

```yaml
ports:
  - "8081:8080"
```

Acesse:

```text
http://localhost:8081
```

### Erro no Oracle

Verifique usuário, senha, rede e acesso ao servidor FIAP. Para não travar a apresentação, use:

```text
HERMES_DB_TARGET=sqlite
```

### Erro de permissão no PowerShell

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Conclusão técnica

O Hermes Orbital Data Pipeline demonstra um fluxo completo de engenharia de dados aplicado ao contexto espacial. A solução coleta dados reais de APIs públicas, gera telemetria orbital simulada, trata e padroniza os dados com Python e Pandas, carrega as informações em banco de dados e executa consultas SQL analíticas. A orquestração com Apache Airflow comprova a automação do processo, enquanto as consultas apoiam decisões relacionadas à priorização de risco orbital, consumo de combustível, remoção de detritos e monitoramento de ativos espaciais.
