-- Плановые показатели по промоутерам/магазинам/SKU
CREATE TABLE IF NOT EXISTS analytics.fact_targets (
    target_id    bigserial PRIMARY KEY,
    period_ym    date NOT NULL,
    scope_level  text NOT NULL CHECK (scope_level IN ('promoter', 'store', 'sku')),
    promoter_id  bigint REFERENCES analytics.dim_user_promoter(promoter_id),
    store_id     bigint REFERENCES analytics.dim_store(store_id),
    sku_id       bigint REFERENCES analytics.dim_product(sku_id),
    plan_units   numeric(18,3) NOT NULL DEFAULT 0,
    plan_revenue numeric(18,2) NOT NULL DEFAULT 0,
    created_at   timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE analytics.fact_targets IS 'Плановые значения продаж.';
COMMENT ON COLUMN analytics.fact_targets.scope_level IS 'Уровень детализации планов.';
COMMENT ON COLUMN analytics.fact_targets.period_ym IS 'Первый день месяца, к которому относится план.';

CREATE INDEX IF NOT EXISTS fact_targets_period_idx ON analytics.fact_targets (period_ym, scope_level);
CREATE UNIQUE INDEX IF NOT EXISTS fact_targets_scope_uniq ON analytics.fact_targets (
    period_ym,
    scope_level,
    COALESCE(promoter_id, 0),
    COALESCE(store_id, 0),
    COALESCE(sku_id, 0)
);
