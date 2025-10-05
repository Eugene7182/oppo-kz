-- Материализованное представление план/факт по промоутерам (месяц)
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_plan_vs_fact_promoter_month AS
WITH plan_data AS (
    SELECT
        date_trunc('month', period_ym)::date AS period_month,
        promoter_id,
        SUM(plan_units)   AS plan_units,
        SUM(plan_revenue) AS plan_revenue
    FROM analytics.fact_targets
    WHERE scope_level = 'promoter'
    GROUP BY 1, 2
),
fact_data AS (
    SELECT
        make_date(msm.year_num, msm.month_num, 1) AS period_month,
        msm.promoter_id,
        SUM(msm.units)   AS fact_units,
        SUM(msm.revenue) AS fact_revenue
    FROM analytics.mv_sales_monthly msm
    GROUP BY 1, 2
)
SELECT
    coalesce(p.period_month, f.period_month) AS period_month,
    extract(year FROM coalesce(p.period_month, f.period_month))::int AS year_num,
    extract(month FROM coalesce(p.period_month, f.period_month))::int AS month_num,
    coalesce(p.promoter_id, f.promoter_id) AS promoter_id,
    p.plan_units,
    p.plan_revenue,
    f.fact_units,
    f.fact_revenue,
    CASE WHEN p.plan_units > 0 THEN f.fact_units / p.plan_units ELSE NULL END AS achievement_units,
    CASE WHEN p.plan_revenue > 0 THEN f.fact_revenue / p.plan_revenue ELSE NULL END AS achievement_revenue,
    CASE WHEN f.fact_units > 0 THEN f.fact_revenue / f.fact_units ELSE NULL END AS asp
FROM plan_data p
FULL OUTER JOIN fact_data f
  ON p.period_month = f.period_month
 AND p.promoter_id = f.promoter_id
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_plan_vs_fact_promoter_month IS 'Сопоставление плана и факта по промоутерам за полный месяц.';

CREATE UNIQUE INDEX IF NOT EXISTS mv_plan_vs_fact_promoter_month_pk ON analytics.mv_plan_vs_fact_promoter_month (
    period_month,
    COALESCE(promoter_id, 0)
);
