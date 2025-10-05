-- Измерение промоутеров
CREATE TABLE IF NOT EXISTS analytics.dim_user_promoter (
    promoter_id   bigserial PRIMARY KEY,
    promoter_code text UNIQUE NOT NULL,
    full_name     text NOT NULL,
    email         text,
    phone_number  text,
    supervisor_id bigint REFERENCES analytics.dim_user_supervisor(supervisor_id),
    hire_date     date,
    dismissal_date date,
    is_active     boolean NOT NULL DEFAULT true
);

COMMENT ON TABLE analytics.dim_user_promoter IS 'Измерение промоутеров и их связей с супервайзерами.';
COMMENT ON COLUMN analytics.dim_user_promoter.supervisor_id IS 'FK на супервайзера.';

CREATE INDEX IF NOT EXISTS dim_user_promoter_supervisor_idx ON analytics.dim_user_promoter (supervisor_id);
