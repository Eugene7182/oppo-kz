-- Измерение регионов
CREATE TABLE IF NOT EXISTS analytics.dim_region (
    region_id   bigserial PRIMARY KEY,
    region_code text UNIQUE NOT NULL,
    region_name text NOT NULL,
    country     text NOT NULL DEFAULT 'Kazakhstan'
);

COMMENT ON TABLE analytics.dim_region IS 'Измерение регионов присутствия.';
COMMENT ON COLUMN analytics.dim_region.region_code IS 'Уникальный код региона (латиница).';
COMMENT ON COLUMN analytics.dim_region.region_name IS 'Отображаемое название региона.';
COMMENT ON COLUMN analytics.dim_region.country IS 'Страна присутствия.';
