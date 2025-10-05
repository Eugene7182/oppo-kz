-- Дата-измерение с признаком полноты недели и месяца
CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_id         date PRIMARY KEY,
    iso_year        smallint NOT NULL,
    iso_week        smallint NOT NULL CHECK (iso_week BETWEEN 1 AND 53),
    month_num       smallint NOT NULL CHECK (month_num BETWEEN 1 AND 12),
    year_num        integer  NOT NULL,
    day_of_week     smallint NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    is_full_week    boolean  NOT NULL DEFAULT false,
    is_full_month   boolean  NOT NULL DEFAULT false,
    day_name        text     NOT NULL,
    week_start_date date     NOT NULL,
    week_end_date   date     NOT NULL,
    month_start_date date    NOT NULL,
    month_end_date   date    NOT NULL
);

COMMENT ON TABLE analytics.dim_date IS 'Измерение календарных дат с информацией о полноте недели и месяца.';
COMMENT ON COLUMN analytics.dim_date.date_id IS 'Первичный ключ (календарная дата).';
COMMENT ON COLUMN analytics.dim_date.iso_year IS 'ISO-год.';
COMMENT ON COLUMN analytics.dim_date.iso_week IS 'ISO-неделя (1-53).';
COMMENT ON COLUMN analytics.dim_date.month_num IS 'Номер месяца (1-12).';
COMMENT ON COLUMN analytics.dim_date.year_num IS 'Грегорианский год.';
COMMENT ON COLUMN analytics.dim_date.day_of_week IS 'Номер дня недели (1=понедельник).';
COMMENT ON COLUMN analytics.dim_date.is_full_week IS 'Флаг полноты ISO-недели в источниках.';
COMMENT ON COLUMN analytics.dim_date.is_full_month IS 'Флаг полноты календарного месяца в источниках.';
COMMENT ON COLUMN analytics.dim_date.day_name IS 'Локализованное название дня недели.';
COMMENT ON COLUMN analytics.dim_date.week_start_date IS 'Дата начала ISO-недели.';
COMMENT ON COLUMN analytics.dim_date.week_end_date IS 'Дата окончания ISO-недели.';
COMMENT ON COLUMN analytics.dim_date.month_start_date IS 'Дата начала месяца.';
COMMENT ON COLUMN analytics.dim_date.month_end_date IS 'Дата окончания месяца.';

CREATE INDEX IF NOT EXISTS dim_date_iso_week_idx ON analytics.dim_date (iso_year, iso_week);
CREATE INDEX IF NOT EXISTS dim_date_month_idx ON analytics.dim_date (year_num, month_num);
