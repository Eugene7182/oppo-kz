-- Материализованное представление period-over-period (WoW/MoM/YoY) с LFL-флагом
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_pops AS
WITH weekly_base AS (
    SELECT
        iso_year,
        iso_week,
        week_start_date,
        week_end_date,
        store_id,
        network_id,
        city_id,
        region_id,
        SUM(units)   AS units,
        SUM(revenue) AS revenue
    FROM analytics.mv_sales_weekly_iso
    GROUP BY
        iso_year,
        iso_week,
        week_start_date,
        week_end_date,
        store_id,
        network_id,
        city_id,
        region_id
),
weekly_metrics AS (
    SELECT
        'week'::text AS period_type,
        wb.week_start_date AS period_start,
        wb.week_end_date   AS period_end,
        wb.store_id,
        wb.network_id,
        wb.city_id,
        wb.region_id,
        wb.units,
        wb.revenue,
        LAG(wb.units) OVER (PARTITION BY wb.store_id ORDER BY wb.week_start_date) AS prev_units,
        LAG(wb.revenue) OVER (PARTITION BY wb.store_id ORDER BY wb.week_start_date) AS prev_revenue,
        LAG(wb.units, 52) OVER (PARTITION BY wb.store_id ORDER BY wb.week_start_date) AS yoy_units,
        LAG(wb.revenue, 52) OVER (PARTITION BY wb.store_id ORDER BY wb.week_start_date) AS yoy_revenue,
        LAG(wb.week_start_date) OVER (PARTITION BY wb.store_id ORDER BY wb.week_start_date) AS prev_period_start,
        LAG(wb.week_end_date) OVER (PARTITION BY wb.store_id ORDER BY wb.week_start_date) AS prev_period_end,
        LAG(wb.week_start_date, 52) OVER (PARTITION BY wb.store_id ORDER BY wb.week_start_date) AS yoy_period_start,
        LAG(wb.week_end_date, 52) OVER (PARTITION BY wb.store_id ORDER BY wb.week_start_date) AS yoy_period_end
    FROM weekly_base wb
),
monthly_base AS (
    SELECT
        make_date(msm.year_num, msm.month_num, 1) AS period_start,
        (make_date(msm.year_num, msm.month_num, 1) + INTERVAL '1 month - 1 day')::date AS period_end,
        msm.store_id,
        msm.network_id,
        msm.city_id,
        msm.region_id,
        SUM(msm.units)   AS units,
        SUM(msm.revenue) AS revenue
    FROM analytics.mv_sales_monthly msm
    GROUP BY
        make_date(msm.year_num, msm.month_num, 1),
        (make_date(msm.year_num, msm.month_num, 1) + INTERVAL '1 month - 1 day')::date,
        msm.store_id,
        msm.network_id,
        msm.city_id,
        msm.region_id
),
monthly_metrics AS (
    SELECT
        'month'::text AS period_type,
        mb.period_start,
        mb.period_end,
        mb.store_id,
        mb.network_id,
        mb.city_id,
        mb.region_id,
        mb.units,
        mb.revenue,
        LAG(mb.units) OVER (PARTITION BY mb.store_id ORDER BY mb.period_start) AS prev_units,
        LAG(mb.revenue) OVER (PARTITION BY mb.store_id ORDER BY mb.period_start) AS prev_revenue,
        LAG(mb.units, 12) OVER (PARTITION BY mb.store_id ORDER BY mb.period_start) AS yoy_units,
        LAG(mb.revenue, 12) OVER (PARTITION BY mb.store_id ORDER BY mb.period_start) AS yoy_revenue,
        LAG(mb.period_start) OVER (PARTITION BY mb.store_id ORDER BY mb.period_start) AS prev_period_start,
        LAG(mb.period_end) OVER (PARTITION BY mb.store_id ORDER BY mb.period_start) AS prev_period_end,
        LAG(mb.period_start, 12) OVER (PARTITION BY mb.store_id ORDER BY mb.period_start) AS yoy_period_start,
        LAG(mb.period_end, 12) OVER (PARTITION BY mb.store_id ORDER BY mb.period_start) AS yoy_period_end
    FROM monthly_base mb
),
combined AS (
    SELECT * FROM weekly_metrics
    UNION ALL
    SELECT * FROM monthly_metrics
)
SELECT
    c.period_type,
    c.period_start,
    c.period_end,
    c.store_id,
    c.network_id,
    c.city_id,
    c.region_id,
    c.units,
    c.revenue,
    CASE WHEN c.prev_units IS NOT NULL THEN c.units - c.prev_units END AS delta_units,
    CASE WHEN c.prev_units IS NOT NULL AND c.prev_units <> 0 THEN (c.units - c.prev_units) / c.prev_units END AS delta_units_pct,
    CASE WHEN c.prev_revenue IS NOT NULL THEN c.revenue - c.prev_revenue END AS delta_revenue,
    CASE WHEN c.prev_revenue IS NOT NULL AND c.prev_revenue <> 0 THEN (c.revenue - c.prev_revenue) / c.prev_revenue END AS delta_revenue_pct,
    CASE WHEN c.yoy_units IS NOT NULL THEN c.units - c.yoy_units END AS delta_units_yoy,
    CASE WHEN c.yoy_units IS NOT NULL AND c.yoy_units <> 0 THEN (c.units - c.yoy_units) / c.yoy_units END AS delta_units_yoy_pct,
    CASE WHEN c.yoy_revenue IS NOT NULL THEN c.revenue - c.yoy_revenue END AS delta_revenue_yoy,
    CASE WHEN c.yoy_revenue IS NOT NULL AND c.yoy_revenue <> 0 THEN (c.revenue - c.yoy_revenue) / c.yoy_revenue END AS delta_revenue_yoy_pct,
    CASE
        WHEN c.prev_period_start IS NULL THEN false
        ELSE (
            SELECT
                CASE
                    WHEN ds.opened_at <= LEAST(c.period_start, COALESCE(c.prev_period_start, c.period_start), COALESCE(c.yoy_period_start, c.period_start))
                     AND (ds.closed_at IS NULL OR ds.closed_at >= COALESCE(c.yoy_period_end, c.period_end))
                    THEN true
                    ELSE false
                END
            FROM analytics.dim_store ds
            WHERE ds.store_id = c.store_id
        )
    END AS is_lfl
FROM combined c
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW analytics.mv_pops IS 'Динамика период-к-периоду (WoW/MoM/YoY) с учётом LFL.';

CREATE INDEX IF NOT EXISTS mv_pops_store_period_idx ON analytics.mv_pops (period_type, period_start, store_id);
