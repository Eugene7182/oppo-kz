-- Материализованное представление обязательств по бонусам
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_bonus_liability_month AS
SELECT
    date_trunc('month', fb.bonus_date)::date AS period_month,
    fb.scheme_id,
    fs.promoter_id,
    fs.store_id,
    ds.network_id,
    ds.city_id,
    dc.region_id,
    SUM(fb.amount) FILTER (WHERE fb.status IN ('pending', 'approved')) AS liability_amount,
    SUM(fb.amount) FILTER (WHERE fb.status = 'paid') AS paid_amount,
    SUM(fb.amount) FILTER (WHERE fb.status = 'rejected') AS rejected_amount,
    SUM(fb.amount) AS total_amount
FROM analytics.fact_bonus fb
JOIN analytics.fact_sales fs ON fs.sale_id = fb.sale_id
JOIN analytics.dim_store ds ON ds.store_id = fs.store_id
JOIN analytics.dim_city dc ON dc.city_id = ds.city_id
GROUP BY
    date_trunc('month', fb.bonus_date)::date,
    fb.scheme_id,
    fs.promoter_id,
    fs.store_id,
    ds.network_id,
    ds.city_id,
    dc.region_id
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_bonus_liability_month IS 'Сумма обязательств по бонусам по месяцам и статусам.';

CREATE UNIQUE INDEX IF NOT EXISTS mv_bonus_liability_month_pk ON analytics.mv_bonus_liability_month (
    period_month,
    scheme_id,
    COALESCE(promoter_id, 0),
    store_id
);
