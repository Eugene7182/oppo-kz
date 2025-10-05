-- Измерение городов, связанных с регионами
CREATE TABLE IF NOT EXISTS analytics.dim_city (
    city_id    bigserial PRIMARY KEY,
    city_code  text UNIQUE NOT NULL,
    city_name  text NOT NULL,
    region_id  bigint NOT NULL REFERENCES analytics.dim_region(region_id),
    timezone   text NOT NULL DEFAULT 'Asia/Almaty'
);

COMMENT ON TABLE analytics.dim_city IS 'Измерение городов внутри регионов.';
COMMENT ON COLUMN analytics.dim_city.city_code IS 'Уникальный код города.';
COMMENT ON COLUMN analytics.dim_city.city_name IS 'Название города.';
COMMENT ON COLUMN analytics.dim_city.timezone IS 'Временная зона города.';

CREATE INDEX IF NOT EXISTS dim_city_region_idx ON analytics.dim_city (region_id);
