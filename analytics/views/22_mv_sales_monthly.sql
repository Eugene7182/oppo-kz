-- Материализованное представление продаж по месяцам (только полные месяцы)
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_sales_monthly AS
WITH monthly AS (
    SELECT
        dd.year_num,
        dd.month_num,
        MIN(dd.month_start_date) AS month_start_date,
        MAX(dd.month_end_date)   AS month_end_date,
        sd.store_id,
        sd.network_id,
        sd.city_id,
        sd.region_id,
        sd.sku_id,
        sd.promoter_id,
        SUM(sd.units)   AS units,
        SUM(sd.revenue) AS revenue,
        BOOL_AND(sd.is_full_month) AS is_full_month
    FROM analytics.mv_sales_daily sd
    JOIN analytics.dim_date dd ON dd.date_id = sd.date_id
    GROUP BY
        dd.year_num,
        dd.month_num,
        sd.store_id,
        sd.network_id,
        sd.city_id,
        sd.region_id,
        sd.sku_id,
        sd.promoter_id
)
SELECT
    year_num,
    month_num,
    month_start_date,
    month_end_date,
    store_id,
    network_id,
    city_id,
    region_id,
    sku_id,
    promoter_id,
    units,
    revenue,
    CASE WHEN units > 0 THEN revenue / units END AS asp
FROM monthly
WHERE is_full_month
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_sales_monthly IS 'Продажи по месяцам. Учитываются только полные месяцы.';

CREATE UNIQUE INDEX IF NOT EXISTS mv_sales_monthly_pk ON analytics.mv_sales_monthly (
    year_num,
    month_num,
    store_id,
    sku_id,
    COALESCE(promoter_id, 0)
);
