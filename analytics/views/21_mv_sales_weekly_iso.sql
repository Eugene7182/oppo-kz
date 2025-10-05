-- Материализованное представление продаж по ISO-неделям (только полные недели)
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_sales_weekly_iso AS
WITH weekly AS (
    SELECT
        dd.iso_year,
        dd.iso_week,
        MIN(dd.week_start_date) AS week_start_date,
        MAX(dd.week_end_date)   AS week_end_date,
        sd.store_id,
        sd.network_id,
        sd.city_id,
        sd.region_id,
        sd.sku_id,
        sd.promoter_id,
        SUM(sd.units)   AS units,
        SUM(sd.revenue) AS revenue,
        BOOL_AND(sd.is_full_week) AS is_full_week
    FROM analytics.mv_sales_daily sd
    JOIN analytics.dim_date dd ON dd.date_id = sd.date_id
    GROUP BY
        dd.iso_year,
        dd.iso_week,
        sd.store_id,
        sd.network_id,
        sd.city_id,
        sd.region_id,
        sd.sku_id,
        sd.promoter_id
)
SELECT
    iso_year,
    iso_week,
    week_start_date,
    week_end_date,
    store_id,
    network_id,
    city_id,
    region_id,
    sku_id,
    promoter_id,
    units,
    revenue,
    CASE WHEN units > 0 THEN revenue / units END AS asp
FROM weekly
WHERE is_full_week
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_sales_weekly_iso IS 'Продажи по ISO-неделям. Учитываются только полные недели.';

CREATE UNIQUE INDEX IF NOT EXISTS mv_sales_weekly_pk ON analytics.mv_sales_weekly_iso (
    iso_year,
    iso_week,
    store_id,
    sku_id,
    COALESCE(promoter_id, 0)
);
