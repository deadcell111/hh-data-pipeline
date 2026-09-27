SELECT
    date_trunc('week', v.published_at)::date AS week_start,
    count(*)                                  AS n_vacancies,
    count(*) FILTER (
        WHERE v.salary_from IS NOT NULL OR v.salary_to IS NOT NULL
    )                                          AS n_with_salary
FROM {{ ref('stg_dim_vacancies') }} v
GROUP BY week_start
