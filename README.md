# Pipeline de Pricing (Airflow)

Substitui o script cron por um DAG que coleta produtos da FakeStore API,
calcula métricas por categoria e grava no PostgreSQL de forma idempotente.


# Estrutura do Projeto

PUCMG-Orquestracao-Workflows-Atividade_1/
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
docker compose exec analytics-db psql -U analytics -d analytics -c "SELECT run_date, COUNT(*) FROM pricing_category_snapshot GROUP BY run_date;"
```

## Decisões de projeto

- **Idempotência:** o snapshot usa `UPSERT` por `(run_date, category)`. O histórico usa
  `ON CONFLICT DO NOTHING` na mesma chave, então reprocessar uma run não duplica linhas.Se a mesma data for reprocessada com preços diferentes, o histórico mantém a primeira gravação e o snapshot recebe a versão nova.
- **Data da run:** `run_date` é a data do `data_interval_end` no fuso de São Paulo, ou seja, o dia em que o painel é consumido.Isso vale para a execução das 06:00. Em uma execução manual, data_interval_end é o momento do disparo, então a data gravada é a do dia do disparo
- **Resiliência:** `buscar_produtos` tem 5 retries com backoff exponencial (30s → até 10min). Erros são relançados com `raise`.
- **Escala:** categorias são descobertas a partir dos dados (`listar_categorias`), sem edição de código.
- **Concorrência:** o mapeamento por categoria roda no `ecommerce_pool`, limitado a 2 slots.
- **Alertas:** callbacks de falha, retry e sucesso. O envio é simulado em log e deve ser trocado por um canal real.

## Esclarecimentos adicionais

- **.gitignore:** impede que arquivos gerados localmente ou sensíveis sejam enviados ao GitHub:
• Caches Python (__pycache__/, *.pyc, .pytest_cache/): criados ao rodar Python e pytest localmente.
• Logs e arquivos do Airflow (logs/, airflow.cfg, airflow.db, *.log): gerados pelo Airflow durante a execução.
• Ambiente e segredos (.env, .venv/, venv/): podem conter senhas ou dependências locais.
- **pytest.ini:** arquivo como alternativa ao $env:PYTHONPATH = "dags", que vale só para a janela atual do PowerShell. O pytest adiciona a pasta dags ao caminho de import, e os testes encontram from pricing.metrics import ... sem configuração manual.Somente para os testes unitários. O Docker não o utiliza
- **requirements.txt:** lista as bibliotecas Python instaladas dentro da imagem Docker. O Dockerfile faz COPY e pip install -r desse arquivo:
• apache-airflow-providers-postgres: fornece o PostgresHook usado em repository.py.
• requests: usado em api_client.py para chamar a FakeStore API.
• pytest: usado para os testes unitários, como está nesse arquivo, ele também entra na imagem. Isso não prejudica o funcionamento.
- **__init__.py:** fica vazio de propósito. Serve para marcar a pasta dags/pricing/ como um pacote Python, o que permite from pricing import alerts, api_client, metrics, repository na DAG e from pricing.metrics import ... nos testes. Em Python 3, o arquivo é tecnicamente opcional, mas mantê-lo é a prática padrão e evita problemas com ferramentas como o pytest.

