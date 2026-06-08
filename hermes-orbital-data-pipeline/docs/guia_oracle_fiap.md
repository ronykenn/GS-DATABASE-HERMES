# Guia Oracle FIAP

Este projeto permite executar a carga dos dados no Oracle usado pela disciplina ou em SQLite local.

## Dados do banco

```text
Host: oracle.fiap.com.br
Porta: 1521
SID: ORCL
```

## Como preencher o `.env`

Cada aluno deve preencher o arquivo `.env` local com as próprias credenciais acadêmicas.

```text
HERMES_DB_TARGET=oracle
ORACLE_USER=rmSEU_RM
ORACLE_PASSWORD=sua_credencial_oracle_fiap
ORACLE_HOST=oracle.fiap.com.br
ORACLE_PORT=1521
ORACLE_SID=ORCL
```

## Padrão de usuário

O usuário normalmente segue o padrão:

```text
rm + número do RM
```

Exemplo fictício:

```text
ORACLE_USER=rm123456
```

## Observações importantes

- Use sempre o próprio RM e a própria credencial acadêmica.
- Não envie o arquivo `.env` para o GitHub.
- Não coloque credenciais reais no README, no PDF, no ZIP ou nos prints.
- Para prints, mostre apenas o arquivo `.env.example` ou o `.env` com os valores ocultos.
- Se o Oracle não conectar, use `HERMES_DB_TARGET=sqlite` para não travar a apresentação.

## Teste rápido

Depois de configurar o `.env`, rode:

```powershell
python scripts\load_database.py
python scripts\run_analytical_queries.py
```

Se estiver usando Docker/Airflow, rode:

```powershell
docker compose up airflow-init
docker compose up
```

Depois acesse:

```text
http://localhost:8080
```

Usuário local do Airflow:

```text
admin
```

Senha local do Airflow:

```text
admin
```
