# Descricao da Solucao

O Projeto Hermes representa uma solucao de dados para a industria espacial, focada em monitoramento orbital e apoio a decisoes para remocao de lixo espacial, extensao de vida util de satelites, taxiamento orbital e reabastecimento em orbita.

## Fontes

- SpaceX API: historico de lancamentos e resultado das missoes.
- Open Notify API: posicao atual da ISS.
- Telemetria Hermes mockada: objetos orbitais, massa, altitude, velocidade, risco de colisao e combustivel estimado.

## Regras de Negocio

A prioridade operacional e calculada pelo `collision_risk_score`:

- `CRITICAL`: risco maior ou igual a 80.
- `HIGH`: risco maior ou igual a 60.
- `MEDIUM`: risco maior ou igual a 40.
- `LOW`: risco abaixo de 40.

A acao recomendada e derivada da prioridade:

- `CRITICAL`: `IMMEDIATE_DEORBIT`.
- `HIGH`: `SCHEDULE_CAPTURE`.
- `MEDIUM`: `MONITOR` ou `ORBITAL_TAXI` para satelites ativos.
- `LOW`: `NO_ACTION`.

## Diferenciais

O pipeline nao quebra quando APIs externas falham. Nesses casos, os extratores usam arquivos em `data/mock` como fallback, mantendo a DAG executavel para apresentacao e avaliacao.
