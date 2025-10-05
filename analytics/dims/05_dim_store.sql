-- Измерение магазинов с привязкой к сети и городу
CREATE TABLE IF NOT EXISTS analytics.dim_store (
    store_id      bigserial PRIMARY KEY,
    store_code    text UNIQUE NOT NULL,
    store_name    text NOT NULL,
    network_id    bigint NOT NULL REFERENCES analytics.dim_network(network_id),
    city_id       bigint NOT NULL REFERENCES analytics.dim_city(city_id),
    opened_at     date NOT NULL,
    closed_at     date,
    is_active     boolean NOT NULL DEFAULT true,
    floor_space_sqm numeric(10,2)
);

COMMENT ON TABLE analytics.dim_store IS 'Измерение торговых точек.';
COMMENT ON COLUMN analytics.dim_store.store_code IS 'Внешний код магазина.';
COMMENT ON COLUMN analytics.dim_store.opened_at IS 'Дата открытия магазина.';
COMMENT ON COLUMN analytics.dim_store.closed_at IS 'Дата закрытия (если применимо).';
COMMENT ON COLUMN analytics.dim_store.is_active IS 'Флаг активности магазина.';
COMMENT ON COLUMN analytics.dim_store.floor_space_sqm IS 'Торговая площадь (кв. м).';

CREATE INDEX IF NOT EXISTS dim_store_network_idx ON analytics.dim_store (network_id);
CREATE INDEX IF NOT EXISTS dim_store_city_idx ON analytics.dim_store (city_id);
CREATE INDEX IF NOT EXISTS dim_store_active_idx ON analytics.dim_store (is_active);
