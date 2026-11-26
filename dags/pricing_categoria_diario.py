from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow.decorators import dag, task, task_group

from pricing import alerts, api_client, metrics, repository
from pricing.operators import ValidarProdutosOperator

TZ = pendulum.timezone("America/Sao_Paulo")

RETRY_POLICY = dict(
    retries=5,
    retry_delay=timedelta(seconds=30),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=10),
)


@dag(
    dag_id="pricing_categoria_diario",
    schedule="0 6 * * *",  # 06:00 America/Sao_Paulo
    start_date=pendulum.datetime(2026, 1, 1, tz="America/Sao_Paulo"),
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "time-dados"},
    tags=["ecommerce", "pricing"],
)
def pricing_categoria_diario():

    # ---------- Topologia 1: INGESTÃO (linear) ----------
    @task_group(group_id="ingestao")
    def ingestao():
        @task(
            task_id="buscar_produtos",
            on_failure_callback=alerts.alerta_falha,
            on_retry_callback=alerts.alerta_retry,
            on_success_callback=alerts.alerta_sucesso,
            **RETRY_POLICY,
        )
        def buscar_produtos():
            return api_client.buscar_produtos()

        produtos = buscar_produtos()

        validar = ValidarProdutosOperator(
            task_id="validar_produtos",
            source_task_id="ingestao.buscar_produtos",
        )
        validar.set_upstream(produtos.operator)
        return validar.output

    # ---------- Topologia 2: ANÁLISE (fan-out por categoria) ----------
    @task_group(group_id="analise")
    def analise(produtos):
        @task
        def listar_categorias(produtos):
            return metrics.listar_categorias(produtos)

        @task(pool="ecommerce_pool")
        def calcular_metricas(produtos, categoria):
            return metrics.calcular_metricas_categoria(produtos, categoria)

        categorias = listar_categorias(produtos)
        return calcular_metricas.partial(produtos=produtos).expand(categoria=categorias)

    # ---------- Topologia 3: PERSISTÊNCIA (fan-in) ----------
    @task_group(group_id="persistencia")
    def persistencia(metricas):
        @task
        def consolidar_e_gravar(metricas, data_interval_end):
            # Fan-in: ao chegar como argumento não mapeado, 'metricas' já é a lista consolidada.
            if not metricas:
                raise ValueError("Nenhuma métrica calculada para gravar")
            run_date = data_interval_end.in_timezone(TZ).date()
            repository.persistir(metricas, run_date)
            return len(metricas)

        return consolidar_e_gravar(metricas)

    produtos = ingestao()
    metricas = analise(produtos)
    persistencia(metricas)


pricing_categoria_diario()