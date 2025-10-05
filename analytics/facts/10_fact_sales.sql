-- Факт продаж с учётом базовых значений и корректировок
CREATE TABLE IF NOT EXISTS analytics.fact_sales (
    sale_id            bigserial PRIMARY KEY,
    date_id            date NOT NULL REFERENCES analytics.dim_date(date_id),
    store_id           bigint NOT NULL REFERENCES analytics.dim_store(store_id),
    sku_id             bigint NOT NULL REFERENCES analytics.dim_product(sku_id),
    promoter_id        bigint REFERENCES analytics.dim_user_promoter(promoter_id),
    base_units         numeric(18,3) NOT NULL DEFAULT 0,
    base_revenue       numeric(18,2) NOT NULL DEFAULT 0,
    correction_units   numeric(18,3) NOT NULL DEFAULT 0,
    correction_revenue numeric(18,2) NOT NULL DEFAULT 0,
    units              numeric(18,3) GENERATED ALWAYS AS (base_units + COALESCE(correction_units, 0)) STORED,
    revenue            numeric(18,2) GENERATED ALWAYS AS (base_revenue + COALESCE(correction_revenue, 0)) STORED,
    created_at         timestamptz NOT NULL DEFAULT now(),
    updated_at         timestamptz NOT NULL DEFAULT now(),
    UNIQUE (date_id, store_id, sku_id, promoter_id)
);

COMMENT ON TABLE analytics.fact_sales IS 'Фактические продажи с учётом корректировок.';
COMMENT ON COLUMN analytics.fact_sales.correction_units IS 'Коррекция продаж (шт).';
COMMENT ON COLUMN analytics.fact_sales.units IS 'Расчёт: base_units + correction_units.';
COMMENT ON COLUMN analytics.fact_sales.revenue IS 'Расчёт: base_revenue + correction_revenue.';

CREATE INDEX IF NOT EXISTS fact_sales_date_idx ON analytics.fact_sales (date_id);
CREATE INDEX IF NOT EXISTS fact_sales_store_idx ON analytics.fact_sales (store_id);
CREATE INDEX IF NOT EXISTS fact_sales_sku_idx ON analytics.fact_sales (sku_id);
CREATE INDEX IF NOT EXISTS fact_sales_promoter_idx ON analytics.fact_sales (promoter_id);

-- Триггер для обновления updated_at
CREATE OR REPLACE FUNCTION analytics.fact_sales_touch_updated_at()
RETURNS trigger AS
$$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_fact_sales_touch_updated_at ON analytics.fact_sales;
CREATE TRIGGER trg_fact_sales_touch_updated_at
    BEFORE UPDATE ON analytics.fact_sales
    FOR EACH ROW
    EXECUTE FUNCTION analytics.fact_sales_touch_updated_at();
