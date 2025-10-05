-- Функции обновления материализованных представлений
CREATE OR REPLACE FUNCTION analytics.refresh_mv_sales_snapshots(p_concurrently boolean DEFAULT true)
RETURNS void AS
$$
BEGIN
    IF p_concurrently THEN
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_sales_daily';
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_sales_weekly_iso';
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_sales_monthly';
    ELSE
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_sales_daily';
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_sales_weekly_iso';
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_sales_monthly';
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION analytics.refresh_mv_plans(p_concurrently boolean DEFAULT true)
RETURNS void AS
$$
BEGIN
    IF p_concurrently THEN
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_plan_vs_fact_promoter_month';
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_plan_vs_fact_region_month';
    ELSE
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_plan_vs_fact_promoter_month';
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_plan_vs_fact_region_month';
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION analytics.refresh_mv_aux(p_concurrently boolean DEFAULT true)
RETURNS void AS
$$
BEGIN
    IF p_concurrently THEN
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_sales_city_month';
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_bonus_liability_month';
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_seasonality_weekly';
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_pops';
        EXECUTE 'REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_anomalies_sales';
    ELSE
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_sales_city_month';
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_bonus_liability_month';
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_seasonality_weekly';
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_pops';
        EXECUTE 'REFRESH MATERIALIZED VIEW analytics.mv_anomalies_sales';
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION analytics.refresh_mv_analytics_full(p_concurrently boolean DEFAULT true)
RETURNS void AS
$$
BEGIN
    PERFORM analytics.refresh_mv_sales_snapshots(p_concurrently);
    PERFORM analytics.refresh_mv_plans(p_concurrently);
    PERFORM analytics.refresh_mv_aux(p_concurrently);
END;
$$ LANGUAGE plpgsql;
