-- Материализованное представление продаж по городам (месяц)
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_sales_city_month AS
SELECT
    make_date(msm.year_num, msm.month_num, 1) AS period_month,
    msm.year_num,
    msm.month_num,
    msm.city_id,
    msm.region_id,
    SUM(msm.units)   AS units,
    SUM(msm.revenue) AS revenue,
    CASE WHEN SUM(msm.units) > 0 THEN SUM(msm.revenue) / SUM(msm.units) END AS asp
FROM analytics.mv_sales_monthly msm
GROUP BY
    make_date(msm.year_num, msm.month_num, 1),
    msm.year_num,
    msm.month_num,
    msm.city_id,
    msm.region_id
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_sales_city_month IS 'Продажи по городам за полный календарный месяц.';

CREATE UNIQUE INDEX IF NOT EXISTS mv_sales_city_month_pk ON analytics.mv_sales_city_month (
    period_month,
    city_id
);
