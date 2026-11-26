# ShopBrasil – Pipeline de Pricing (Airflow)

Substitui o script cron por um DAG que coleta produtos da FakeStore API,
calcula métricas por categoria e grava no PostgreSQL de forma idempotente.


# Estrutura do Projeto

shopbrasil-pricing-pipeline/
├──.gitattributes
├──.gitignore
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── Requirements.txt
├── README.md
├── sql/
│   └── schema.sql
├── dags/
│   ├── pricing_categoria_diario.py
│   └── pricing/
│       ├── __init__.py
│       ├── api_client.py
│       ├── metrics.py
│       ├── repository.py
│       ├── alerts.py
│       └── operators.py
└── tests/
    └── test_metrics.py


## Como rodar

```bash
docker compose up -d --build
```

- Airflow UI: http://localhost:8080 (usuário `admin` / senha `admin`)
- Banco analítico: `localhost:5433` (usuário/senha/base: `analytics`)
- Ative e dispare o DAG `pricing_categoria_diario` na UI, ou aguarde as 06:00 (America/Sao_Paulo).

Consulta de validação:
```sql
SELECT * FROM pricing_category_snapshot ORDER BY run_date DESC, category;
```

## Testes

```bash
PYTHONPATH=dags pytest tests/
```

## Decisões de projeto

- **Idempotência:** o snapshot usa `UPSERT` por `(run_date, category)`. O histórico usa
  `ON CONFLICT DO NOTHING` na mesma chave, então reprocessar uma run não duplica linhas.Se a mesma data for reprocessada com preços diferentes, o histórico mantém a primeira gravação e o snapshot recebe a versão nova.
- **Data da run:** `run_date` é a data do `data_interval_end` no fuso de São Paulo, ou seja, o dia em que o painel é consumido.Isso vale para a execução das 06:00. Em uma execução manual, data_interval_end é o momento do disparo, então a data gravada é a do dia do disparo
- **Resiliência:** `buscar_produtos` tem 5 retries com backoff exponencial (30s → até 10min). Erros são relançados com `raise`.
- **Escala:** categorias são descobertas a partir dos dados (`listar_categorias`), sem edição de código.
- **Concorrência:** o mapeamento por categoria roda no `ecommerce_pool`, limitado a 2 slots.
- **Alertas:** callbacks de falha, retry e sucesso. O envio é simulado em log e deve ser trocado por um canal real.