-- Измерение супервайзеров
CREATE TABLE IF NOT EXISTS analytics.dim_user_supervisor (
    supervisor_id bigserial PRIMARY KEY,
    supervisor_code text UNIQUE NOT NULL,
    full_name     text NOT NULL,
    email         text,
    phone_number  text,
    is_active     boolean NOT NULL DEFAULT true
);

COMMENT ON TABLE analytics.dim_user_supervisor IS 'Измерение пользователей-супервайзеров.';
