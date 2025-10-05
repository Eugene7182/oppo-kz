-- Измерение сетей (retail networks)
CREATE TABLE IF NOT EXISTS analytics.dim_network (
    network_id   bigserial PRIMARY KEY,
    network_code text UNIQUE NOT NULL,
    network_name text NOT NULL,
    is_active    boolean NOT NULL DEFAULT true
);

COMMENT ON TABLE analytics.dim_network IS 'Измерение розничных сетей партнёров.';
COMMENT ON COLUMN analytics.dim_network.network_code IS 'Код сети, соответствующий внешним системам.';
COMMENT ON COLUMN analytics.dim_network.is_active IS 'Флаг активности сети.';
