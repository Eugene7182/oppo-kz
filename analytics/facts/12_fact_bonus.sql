-- Факты по бонусным выплатам
CREATE TABLE IF NOT EXISTS analytics.fact_bonus (
    bonus_id   bigserial PRIMARY KEY,
    sale_id    bigint NOT NULL REFERENCES analytics.fact_sales(sale_id),
    scheme_id  bigint NOT NULL,
    bonus_date date NOT NULL,
    amount     numeric(18,2) NOT NULL,
    status     text NOT NULL CHECK (status IN ('pending', 'approved', 'rejected', 'paid')),
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE analytics.fact_bonus IS 'Выплаты по бонусным схемам.';
COMMENT ON COLUMN analytics.fact_bonus.scheme_id IS 'Ссылка на бонусную сетку.';

CREATE INDEX IF NOT EXISTS fact_bonus_status_idx ON analytics.fact_bonus (status);
CREATE INDEX IF NOT EXISTS fact_bonus_date_idx ON analytics.fact_bonus (bonus_date);
