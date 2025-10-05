-- Материализованное представление сезонности (недели)
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_seasonality_weekly AS
WITH weekly AS (
    SELECT
        iso_year,
        iso_week,
        week_start_date,
        week_end_date,
        store_id,
        sku_id,
        SUM(units)   AS units,
        SUM(revenue) AS revenue
    FROM analytics.mv_sales_weekly_iso
    GROUP BY
        iso_year,
        iso_week,
        week_start_date,
        week_end_date,
        store_id,
        sku_id
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
    AVG(units) OVER (
        PARTITION BY store_id, sku_id
        ORDER BY week_start_date
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS moving_avg_4w,
    AVG(units) OVER (
        PARTITION BY store_id, sku_id
        ORDER BY week_start_date
        ROWS BETWEEN 7 PRECEDING AND CURRENT ROW
    ) AS moving_avg_8w,
    CASE
        WHEN AVG(units) OVER (
            PARTITION BY store_id, sku_id
            ORDER BY week_start_date
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) > 0
        THEN units / AVG(units) OVER (
            PARTITION BY store_id, sku_id
            ORDER BY week_start_date
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        )
        ELSE NULL
    END AS seasonality_index
FROM weekly
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_seasonality_weekly IS 'Сезонность продаж: скользящее среднее 4/8 недель и индекс сезонности.';

CREATE UNIQUE INDEX IF NOT EXISTS mv_seasonality_weekly_pk ON analytics.mv_seasonality_weekly (
    iso_year,
    iso_week,
    store_id,
    sku_id
);
