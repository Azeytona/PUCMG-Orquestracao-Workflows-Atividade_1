from __future__ import annotations

from datetime import date

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values

CONN_ID = "ecommerce_analytics"

SQL_SNAPSHOT = """
    INSERT INTO pricing_category_snapshot
        (run_date, category, avg_price, min_price, max_price, product_count)
    VALUES %s
    ON CONFLICT (run_date, category) DO UPDATE SET
        avg_price     = EXCLUDED.avg_price,
        min_price     = EXCLUDED.min_price,
        max_price     = EXCLUDED.max_price,
        product_count = EXCLUDED.product_count,
        loaded_at     = now()
"""

SQL_HISTORY = """
    INSERT INTO pricing_category_history
        (run_date, category, avg_price, min_price, max_price, product_count)
    VALUES %s
    ON CONFLICT (run_date, category) DO NOTHING
"""


def persistir(metricas: list[dict], run_date: date) -> None:
    linhas = [
        (run_date, m["category"], m["avg_price"], m["min_price"], m["max_price"], m["product_count"])
        for m in metricas
    ]
    conn = PostgresHook(postgres_conn_id=CONN_ID).get_conn()
    try:
        # 'with conn' faz commit único: snapshot e histórico são atômicos.
        with conn, conn.cursor() as cur:
            execute_values(cur, SQL_SNAPSHOT, linhas)
            execute_values(cur, SQL_HISTORY, linhas)
    finally:
        conn.close()