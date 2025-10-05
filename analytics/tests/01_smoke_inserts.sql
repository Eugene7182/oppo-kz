-- Минимальные данные для проверки витрин
INSERT INTO analytics.dim_region (region_code, region_name)
VALUES ('ALM', 'Алматы')
ON CONFLICT (region_code) DO NOTHING;

INSERT INTO analytics.dim_city (city_code, city_name, region_id)
SELECT 'ALM_CITY', 'Алматы', region_id
FROM analytics.dim_region
WHERE region_code = 'ALM'
ON CONFLICT (city_code) DO NOTHING;

INSERT INTO analytics.dim_network (network_code, network_name)
VALUES ('SIESTA', 'Siesta Retail')
ON CONFLICT (network_code) DO NOTHING;

INSERT INTO analytics.dim_user_supervisor (supervisor_code, full_name, email)
VALUES ('SUP-001', 'Иван Иванов', 'supervisor@example.com')
ON CONFLICT (supervisor_code) DO NOTHING;

INSERT INTO analytics.dim_user_promoter (promoter_code, full_name, email, supervisor_id, hire_date)
SELECT 'PROMO-001', 'Алия Серикова', 'promoter@example.com', supervisor_id, DATE '2023-01-01'
FROM analytics.dim_user_supervisor
WHERE supervisor_code = 'SUP-001'
ON CONFLICT (promoter_code) DO NOTHING;

INSERT INTO analytics.dim_product (sku_code, sku_name, category, product_group, valid_from)
VALUES ('SKU-001', 'OPPO Reno', 'Smartphones', 'Reno', DATE '2023-01-01')
ON CONFLICT (sku_code) DO NOTHING;

INSERT INTO analytics.dim_store (store_code, store_name, network_id, city_id, opened_at, is_active)
SELECT 'STORE-001', 'Siesta Dostyk', dn.network_id, dc.city_id, DATE '2022-01-01', true
FROM analytics.dim_network dn
CROSS JOIN analytics.dim_city dc
WHERE dn.network_code = 'SIESTA' AND dc.city_code = 'ALM_CITY'
ON CONFLICT (store_code) DO NOTHING;

-- Даты недели 2024-01-01..2024-01-07
INSERT INTO analytics.dim_date (
    date_id, iso_year, iso_week, month_num, year_num, day_of_week,
    is_full_week, is_full_month, day_name,
    week_start_date, week_end_date, month_start_date, month_end_date
)
VALUES
    (DATE '2024-01-01', 2024, 1, 1, 2024, 1, true, true, 'Понедельник', DATE '2024-01-01', DATE '2024-01-07', DATE '2024-01-01', DATE '2024-01-31'),
    (DATE '2024-01-02', 2024, 1, 1, 2024, 2, true, true, 'Вторник',    DATE '2024-01-01', DATE '2024-01-07', DATE '2024-01-01', DATE '2024-01-31'),
    (DATE '2024-01-03', 2024, 1, 1, 2024, 3, true, true, 'Среда',       DATE '2024-01-01', DATE '2024-01-07', DATE '2024-01-01', DATE '2024-01-31'),
    (DATE '2024-01-04', 2024, 1, 1, 2024, 4, true, true, 'Четверг',     DATE '2024-01-01', DATE '2024-01-07', DATE '2024-01-01', DATE '2024-01-31'),
    (DATE '2024-01-05', 2024, 1, 1, 2024, 5, true, true, 'Пятница',     DATE '2024-01-01', DATE '2024-01-07', DATE '2024-01-01', DATE '2024-01-31'),
    (DATE '2024-01-06', 2024, 1, 1, 2024, 6, true, true, 'Суббота',     DATE '2024-01-01', DATE '2024-01-07', DATE '2024-01-01', DATE '2024-01-31'),
    (DATE '2024-01-07', 2024, 1, 1, 2024, 7, true, true, 'Воскресенье', DATE '2024-01-01', DATE '2024-01-07', DATE '2024-01-01', DATE '2024-01-31')
ON CONFLICT (date_id) DO NOTHING;

-- Факт продаж 7 дней по 10 юнитов, 100000 тг в день
INSERT INTO analytics.fact_sales (date_id, store_id, sku_id, promoter_id, base_units, base_revenue)
SELECT
    dd.date_id,
    ds.store_id,
    dp.sku_id,
    dup.promoter_id,
    10,
    100000
FROM analytics.dim_date dd
CROSS JOIN analytics.dim_store ds
CROSS JOIN analytics.dim_product dp
CROSS JOIN analytics.dim_user_promoter dup
WHERE dd.date_id BETWEEN DATE '2024-01-01' AND DATE '2024-01-07';

-- План на январь по промоутеру и магазину
INSERT INTO analytics.fact_targets (period_ym, scope_level, promoter_id, plan_units, plan_revenue)
SELECT DATE '2024-01-01', 'promoter', promoter_id, 300, 3000000
FROM analytics.dim_user_promoter
ON CONFLICT DO NOTHING;

INSERT INTO analytics.fact_targets (period_ym, scope_level, store_id, plan_units, plan_revenue)
SELECT DATE '2024-01-01', 'store', store_id, 300, 3000000
FROM analytics.dim_store
ON CONFLICT DO NOTHING;

-- Бонусы
INSERT INTO analytics.fact_bonus (sale_id, scheme_id, bonus_date, amount, status)
SELECT fs.sale_id, 1, DATE '2024-01-05', 15000, 'approved'
FROM analytics.fact_sales fs
WHERE fs.date_id = DATE '2024-01-05'
LIMIT 1;

-- Рефреш витрин (после первичной загрузки выполнить без CONCURRENTLY)
-- REFRESH MATERIALIZED VIEW analytics.mv_sales_daily;
-- REFRESH MATERIALIZED VIEW analytics.mv_sales_weekly_iso;
-- REFRESH MATERIALIZED VIEW analytics.mv_sales_monthly;
-- REFRESH MATERIALIZED VIEW analytics.mv_plan_vs_fact_promoter_month;
-- REFRESH MATERIALIZED VIEW analytics.mv_plan_vs_fact_region_month;
-- REFRESH MATERIALIZED VIEW analytics.mv_sales_city_month;
-- REFRESH MATERIALIZED VIEW analytics.mv_bonus_liability_month;
-- REFRESH MATERIALIZED VIEW analytics.mv_seasonality_weekly;
-- REFRESH MATERIALIZED VIEW analytics.mv_pops;
-- REFRESH MATERIALIZED VIEW analytics.mv_anomalies_sales;
