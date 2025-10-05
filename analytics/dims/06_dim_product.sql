-- Измерение продуктов (SKU)
CREATE TABLE IF NOT EXISTS analytics.dim_product (
    sku_id        bigserial PRIMARY KEY,
    sku_code      text UNIQUE NOT NULL,
    sku_name      text NOT NULL,
    category      text,
    product_group text,
    valid_from    date,
    valid_to      date
);

COMMENT ON TABLE analytics.dim_product IS 'Измерение SKU/продуктов.';
COMMENT ON COLUMN analytics.dim_product.valid_from IS 'Начало действия прайс-листа.';
COMMENT ON COLUMN analytics.dim_product.valid_to IS 'Окончание действия прайс-листа.';

CREATE INDEX IF NOT EXISTS dim_product_category_idx ON analytics.dim_product (category);
