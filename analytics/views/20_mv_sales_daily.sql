-- Материализованное представление дневных продаж
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_sales_daily AS
SELECT
    fs.date_id,
    dd.iso_year,
    dd.iso_week,
    dd.month_num,
    dd.year_num,
    fs.store_id,
    ds.network_id,
    ds.city_id,
    dc.region_id,
    fs.sku_id,
    fs.promoter_id,
    SUM(fs.units)    AS units,
    SUM(fs.revenue)  AS revenue,
    CASE WHEN SUM(fs.units) > 0 THEN SUM(fs.revenue) / SUM(fs.units) END AS asp,
    dd.is_full_week,
    dd.is_full_month
FROM analytics.fact_sales fs
JOIN analytics.dim_date dd ON dd.date_id = fs.date_id
JOIN analytics.dim_store ds ON ds.store_id = fs.store_id
JOIN analytics.dim_city dc ON dc.city_id = ds.city_id
GROUP BY
    fs.date_id,
    dd.iso_year,
    dd.iso_week,
    dd.month_num,
    dd.year_num,
    fs.store_id,
    ds.network_id,
    ds.city_id,
    dc.region_id,
    fs.sku_id,
    fs.promoter_id,
    dd.is_full_week,
    dd.is_full_month
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_sales_daily IS 'Дневные продажи с ASP и флагами полноты периодов.';

CREATE UNIQUE INDEX IF NOT EXISTS mv_sales_daily_pk ON analytics.mv_sales_daily (
    date_id,
    store_id,
    sku_id,
    COALESCE(promoter_id, 0)
);
CREATE INDEX IF NOT EXISTS mv_sales_daily_region_idx ON analytics.mv_sales_daily (region_id, city_id);
