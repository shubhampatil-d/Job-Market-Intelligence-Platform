    CREATE TABLE IF NOT EXISTS analytics.fact_jobs (
    id SERIAL PRIMARY KEY,

    job_id VARCHAR(100) NOT NULL UNIQUE,

    job_title VARCHAR(500) NOT NULL,
    employer_name VARCHAR(300) NOT NULL,

    employer_logo TEXT,
    job_publisher VARCHAR(300),

    job_employment_type VARCHAR(100),
    job_employment_types TEXT,

    job_description TEXT,

    job_city VARCHAR(200),
    job_state VARCHAR(200),
    job_country VARCHAR(100),

    job_latitude DOUBLE PRECISION,
    job_longitude DOUBLE PRECISION,

    job_min_salary DOUBLE PRECISION,
    job_max_salary DOUBLE PRECISION,

    job_salary_period VARCHAR(50),
    job_salary_currency VARCHAR(20),

    job_posted_at VARCHAR(100),
    job_posted_at_datetime_utc TIMESTAMPTZ,

    job_is_remote BOOLEAN NOT NULL DEFAULT FALSE,
    job_apply_is_direct BOOLEAN NOT NULL DEFAULT FALSE,

    job_highlights TEXT,

    apply_options_count INTEGER NOT NULL DEFAULT 0,

    job_apply_link TEXT,
    job_google_link TEXT
);


CREATE INDEX IF NOT EXISTS idx_fact_jobs_employer
    ON analytics.fact_jobs(employer_name);


CREATE INDEX IF NOT EXISTS idx_fact_jobs_city
    ON analytics.fact_jobs(job_city);


CREATE INDEX IF NOT EXISTS idx_fact_jobs_country
    ON analytics.fact_jobs(job_country);


CREATE INDEX IF NOT EXISTS idx_fact_jobs_remote
    ON analytics.fact_jobs(job_is_remote);


CREATE INDEX IF NOT EXISTS idx_fact_jobs_posted
    ON analytics.fact_jobs(job_posted_at_datetime_utc);