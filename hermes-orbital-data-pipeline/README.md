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

## Objetivo

Automatizar um fluxo completo de engenharia de dados usando **Apache Airflow**:

```text
Fonte de dados -> Extração -> Raw files -> Transformação Pandas -> Banco de dados -> Consultas SQL -> Resultados analíticos
```

O pipeline faz extração de dados espaciais, geração de telemetria orbital simulada, tratamento com Pandas, carga em banco de dados e execução de consultas analíticas SQL.

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

Se uma API falhar, os scripts usam fallback local em `data/mock`.

## Estrutura do projeto

```text
hermes-orbital-data-pipeline/
├── dags/
│   └── hermes_orbital_pipeline_dag.py
├── scripts/
├── sql/
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

Fluxo:

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

Regras:

| collision_risk_score | priority_level | recommended_action |
|---|---|---|
| >= 80 | CRITICAL | IMMEDIATE_DEORBIT |
| >= 60 e < 80 | HIGH | SCHEDULE_CAPTURE |
| >= 40 e < 60 | MEDIUM | MONITOR |
| < 40 | LOW | NO_ACTION |

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
- internet para APIs externas;
- acesso ao Oracle FIAP, caso a equipe use Oracle.

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

Criar o arquivo `.env` local:

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

Para configurar o Oracle FIAP, consulte:

```text
docs/guia_oracle_fiap.md
```

O arquivo `.env` não deve ser enviado ao GitHub.

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

```powershell
copy .env.example .env
docker compose up airflow-init
docker compose up
```

Acessar:

```text
http://localhost:8080
```

Login local do Airflow:

```text
usuário: admin
senha: admin
```

## Desabilitar SpaceX API (opcional)

Se a API da SpaceX estiver indisponível ou você preferir usar sempre os dados de fallback locais (recomendado para apresentações ou testes offline), defina a variável de ambiente `USE_SPACEX_API` no arquivo `.env`:

```text
USE_SPACEX_API=false
```

Com `USE_SPACEX_API=false` o script `scripts/extract_spacex.py` não fará chamadas externas e carregará diretamente `data/mock/spacex_launches_fallback.json`. Para habilitar a chamada ao serviço ao vivo, defina `USE_SPACEX_API=true`.

Observações:
- O operador `extract_spacex_launches` na DAG tem um `execution_timeout` curto e a requisição foi ajustada para timeout de 10s, de modo que falhas na API não travem longamente a execução.
- Certifique-se de que `data/mock/spacex_launches_fallback.json` exista no repositório/container quando usar o fallback.


No Airflow:

1. procurar a DAG `hermes_orbital_pipeline`;
2. ativar a DAG;
3. clicar em `Trigger DAG`;
4. acompanhar pela `Grid View`, `Graph View` e logs.

Parar os containers:

```powershell
docker compose down
```

Reiniciar do zero, apagando volume do Postgres do Airflow:

```powershell
docker compose down -v
```

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

1. estrutura do projeto no VS Code;
2. arquivo `dags/hermes_orbital_pipeline_dag.py`;
3. terminal com `docker compose up` rodando;
4. tela inicial do Airflow com a DAG `hermes_orbital_pipeline`;
5. DAG ativada;
6. `Graph View` da DAG;
7. `Grid View` ou `Graph View` com todas as tarefas verdes;
8. logs de `extract_spacex_launches` ou `extract_iss_position`;
9. logs de `generate_mock_telemetry`;
10. logs de `transform_telemetry_data`;
11. logs de `load_to_database`;
12. logs de `run_analytical_queries`;
13. pasta `data/raw`;
14. pasta `data/processed`;
15. pasta `data/processed/query_results`;
16. banco populado no Oracle, SQLite, DBeaver, SQL Developer ou DB Browser;
17. consulta analítica de agrupamento;
18. ranking de risco orbital.

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

Depois acesse:

```text
http://localhost:8081
```

### Erro no Oracle

Verifique o `.env`, o usuário Oracle FIAP, a senha acadêmica, a rede e o acesso ao host `oracle.fiap.com.br`. Para não travar a apresentação, use:

```text
HERMES_DB_TARGET=sqlite
```

### Erro de permissão no PowerShell

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Conclusão técnica

O Hermes Orbital Data Pipeline demonstra um fluxo completo de engenharia de dados aplicado ao contexto espacial. A solução coleta dados reais de APIs públicas, gera telemetria orbital simulada, trata e padroniza os dados com Python e Pandas, carrega as informações em banco de dados e executa consultas SQL analíticas. A orquestração com Apache Airflow comprova a automação do processo, enquanto as consultas apoiam decisões relacionadas à priorização de risco orbital, consumo de combustível, remoção de detritos e monitoramento de ativos espaciais.
