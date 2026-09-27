SELECT
    s.skill_name,
    v.currency,
    count(*)                       AS n_vacancies,
    round(avg(v.salary_from), 0)   AS avg_salary_from,
    round(avg(v.salary_to), 0)     AS avg_salary_to
FROM {{ ref('stg_vacancy_skills') }} s
JOIN {{ ref('stg_dim_vacancies') }} v ON v.vacancy_id = s.vacancy_id
WHERE v.salary_from IS NOT NULL OR v.salary_to IS NOT NULL
GROUP BY s.skill_name, v.currency
