-- Материализованное представление план/факт по регионам (месяц)
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_plan_vs_fact_region_month AS
WITH plan_store AS (
    SELECT
        date_trunc('month', ft.period_ym)::date AS period_month,
        dc.region_id,
        SUM(ft.plan_units)   AS plan_units,
        SUM(ft.plan_revenue) AS plan_revenue
    FROM analytics.fact_targets ft
    JOIN analytics.dim_store ds ON ds.store_id = ft.store_id
    JOIN analytics.dim_city dc ON dc.city_id = ds.city_id
    WHERE ft.scope_level = 'store'
    GROUP BY 1, 2
),
fact_region AS (
    SELECT
        make_date(msm.year_num, msm.month_num, 1) AS period_month,
        msm.region_id,
        SUM(msm.units)   AS fact_units,
        SUM(msm.revenue) AS fact_revenue
    FROM analytics.mv_sales_monthly msm
    GROUP BY 1, 2
)
SELECT
    coalesce(p.period_month, f.period_month) AS period_month,
    extract(year FROM coalesce(p.period_month, f.period_month))::int AS year_num,
    extract(month FROM coalesce(p.period_month, f.period_month))::int AS month_num,
    coalesce(p.region_id, f.region_id) AS region_id,
    p.plan_units,
    p.plan_revenue,
    f.fact_units,
    f.fact_revenue,
    CASE WHEN p.plan_units > 0 THEN f.fact_units / p.plan_units ELSE NULL END AS achievement_units,
    CASE WHEN p.plan_revenue > 0 THEN f.fact_revenue / p.plan_revenue ELSE NULL END AS achievement_revenue
FROM plan_store p
FULL OUTER JOIN fact_region f
  ON p.period_month = f.period_month
 AND p.region_id = f.region_id
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_plan_vs_fact_region_month IS 'Сопоставление плана и факта по регионам за полный месяц.';

CREATE UNIQUE INDEX IF NOT EXISTS mv_plan_vs_fact_region_month_pk ON analytics.mv_plan_vs_fact_region_month (
    period_month,
    COALESCE(region_id, 0)
);
