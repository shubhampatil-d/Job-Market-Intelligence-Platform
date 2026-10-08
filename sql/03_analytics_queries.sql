]-- 1. Total jobs
SELECT COUNT(*) AS total_jobs
FROM analytics.fact_jobs;


-- 2. Jobs by company
SELECT
    employer_name,
    COUNT(*) AS job_count
FROM analytics.fact_jobs
GROUP BY employer_name
ORDER BY job_count DESC;


-- 3. Jobs by location
SELECT
    job_city,
    job_state,
    COUNT(*) AS job_count
FROM analytics.fact_jobs
GROUP BY job_city, job_state
ORDER BY job_count DESC;


-- 4. Remote vs non-remote
SELECT
    job_is_remote,
    COUNT(*) AS job_count
FROM analytics.fact_jobs
GROUP BY job_is_remote;


-- 5. Employment type
SELECT
    job_employment_type,
    COUNT(*) AS job_count
FROM analytics.fact_jobs
GROUP BY job_employment_type
ORDER BY job_count DESC;


-- 6. Jobs with salary information
SELECT
    COUNT(*) AS jobs_with_salary
FROM analytics.fact_jobs
WHERE job_min_salary IS NOT NULL
   OR job_max_salary IS NOT NULL;


-- 7. Average maximum salary
SELECT
    AVG(job_max_salary) AS average_max_salary
FROM analytics.fact_jobs
WHERE job_max_salary IS NOT NULL;


-- 8. Most recent jobs
SELECT
    job_title,
    employer_name,
    job_city,
    job_posted_at_datetime_utc
FROM analytics.fact_jobs
ORDER BY job_posted_at_datetime_utc DESC NULLS LAST
LIMIT 20;