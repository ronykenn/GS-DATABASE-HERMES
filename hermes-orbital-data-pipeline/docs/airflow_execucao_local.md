# Execucao Local do Airflow Sem Docker

Este projeto pode ser executado no Airflow sem Docker, usando a instalacao da `.venv`.

## 1. Abrir a pasta do projeto

```powershell
cd C:\Users\hyeon\Desktop\GS-DATABASE\hermes-orbital-data-pipeline
.venv\Scripts\Activate.ps1
```

## 2. Configurar o Airflow local

```powershell
$env:AIRFLOW_HOME="$PWD\.airflow"
$env:AIRFLOW__CORE__LOAD_EXAMPLES="False"
$env:AIRFLOW__CORE__DAGS_FOLDER="$PWD\dags"
$env:PYTHONPATH="$PWD\scripts"
$env:AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:////$($PWD.Path -replace '\\','/')/.airflow/airflow.db"
```

## 3. Inicializar o banco do Airflow

```powershell
airflow db migrate
```

## 4. Criar usuario admin

```powershell
airflow users create --username admin --password admin --firstname Hermes --lastname FIAP --role Admin --email admin@example.com
```

## 5. Rodar o webserver

Em um terminal:

```powershell
.venv\Scripts\Activate.ps1
$env:AIRFLOW_HOME="$PWD\.airflow"
$env:AIRFLOW__CORE__LOAD_EXAMPLES="False"
$env:AIRFLOW__CORE__DAGS_FOLDER="$PWD\dags"
$env:PYTHONPATH="$PWD\scripts"
$env:AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:////$($PWD.Path -replace '\\','/')/.airflow/airflow.db"
airflow webserver --port 8080
```

## 6. Rodar o scheduler

Em outro terminal:

```powershell
.venv\Scripts\Activate.ps1
$env:AIRFLOW_HOME="$PWD\.airflow"
$env:AIRFLOW__CORE__LOAD_EXAMPLES="False"
$env:AIRFLOW__CORE__DAGS_FOLDER="$PWD\dags"
$env:PYTHONPATH="$PWD\scripts"
$env:AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:////$($PWD.Path -replace '\\','/')/.airflow/airflow.db"
airflow scheduler
```

## 7. Abrir a interface

Abrir:

```text
http://localhost:8080
```

Login:

```text
usuario: admin
senha: admin
```

## 8. Executar a DAG

Na interface:

1. localizar a DAG `hermes_orbital_pipeline`;
2. ativar a DAG;
3. clicar em `Trigger DAG`;
4. abrir `Graph View`;
5. capturar os prints exigidos para o PDF.

## Prints recomendados

- lista de DAGs com `hermes_orbital_pipeline`;
- graph view com o fluxo completo;
- grid view com todas as tasks em verde;
- detalhe da task `load_to_database`;
- detalhe da task `run_analytical_queries`.
