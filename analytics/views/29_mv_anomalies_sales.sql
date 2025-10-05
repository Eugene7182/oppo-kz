-- Материализованное представление аномалий продаж (по residuals, |z|>=3)
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_anomalies_sales AS
WITH residuals AS (
    SELECT
        sw.iso_year,
        sw.iso_week,
        sw.week_start_date,
        sw.week_end_date,
        sw.store_id,
        sw.sku_id,
        sw.units,
        sw.revenue,
        sw.moving_avg_4w,
        sw.moving_avg_8w,
        sw.seasonality_index,
        (sw.units - COALESCE(sw.moving_avg_4w, 0)) AS residual_units,
        STDDEV_SAMP(sw.units - COALESCE(sw.moving_avg_4w, 0)) OVER (PARTITION BY sw.store_id, sw.sku_id) AS residual_stddev
    FROM analytics.mv_seasonality_weekly sw
),
scored AS (
    SELECT
        r.*,
        CASE WHEN r.residual_stddev IS NOT NULL AND r.residual_stddev <> 0 THEN r.residual_units / r.residual_stddev END AS z_score
    FROM residuals r
)
SELECT
    iso_year,
    iso_week,
    week_start_date,
    week_end_date,
    store_id,
    sku_id,
    units,
    revenue,
    moving_avg_4w,
    moving_avg_8w,
    seasonality_index,
    residual_units,
    residual_stddev,
    z_score
FROM scored
WHERE z_score IS NOT NULL AND ABS(z_score) >= 3
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_anomalies_sales IS 'Аномальные продажи (|z|>=3) на основании отклонений от скользящего среднего.';

CREATE INDEX IF NOT EXISTS mv_anomalies_sales_store_idx ON analytics.mv_anomalies_sales (store_id, sku_id, week_start_date);
