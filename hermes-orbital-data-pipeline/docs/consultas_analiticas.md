# Consultas Analiticas

As consultas estao em:

- `sql/03_analytical_queries_oracle.sql`
- `sql/04_analytical_queries_sqlite.sql`

## Consultas Implementadas

1. Quantidade de objetos orbitais por tipo.
2. Media, minimo e maximo do risco de colisao por zona orbital.
3. Ranking dos 10 objetos com maior risco de colisao.
4. Quantidade de missoes recomendadas por tipo de acao.
5. Consumo total de combustivel estimado por nivel de prioridade.
6. Comparacao entre lancamentos SpaceX bem-sucedidos e malsucedidos por ano.
7. Ultimas posicoes registradas da ISS.

## Saidas

Ao executar `python scripts/run_analytical_queries.py` com SQLite, os resultados sao exportados em CSV para:

```text
data/processed/query_results/
```

Esses arquivos podem ser usados nos prints da apresentacao e na documentacao final em PDF.
