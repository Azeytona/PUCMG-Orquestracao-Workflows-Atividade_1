-- Snapshot idempotente: uma linha por (dia, categoria). Reprocessar sobrescreve.
CREATE TABLE IF NOT EXISTS pricing_category_snapshot (
    run_date      DATE          NOT NULL,
    category      TEXT          NOT NULL,
    avg_price     NUMERIC(12,2) NOT NULL,
    min_price     NUMERIC(12,2) NOT NULL,
    max_price     NUMERIC(12,2) NOT NULL,
    product_count INTEGER       NOT NULL,
    loaded_at     TIMESTAMPTZ   NOT NULL DEFAULT now(),
    PRIMARY KEY (run_date, category)
);

-- Histórico em modo append por execução. A chave (dia, categoria) impede
-- duplicar a linha quando a mesma execução é reprocessada.
CREATE TABLE IF NOT EXISTS pricing_category_history (
    run_date      DATE          NOT NULL,
    category      TEXT          NOT NULL,
    avg_price     NUMERIC(12,2) NOT NULL,
    min_price     NUMERIC(12,2) NOT NULL,
    max_price     NUMERIC(12,2) NOT NULL,
    product_count INTEGER       NOT NULL,
    inserted_at   TIMESTAMPTZ   NOT NULL DEFAULT now(),
    PRIMARY KEY (run_date, category)
);