SELECT
    e.name    AS employer,
    count(*)  AS n_vacancies
FROM {{ ref('stg_dim_vacancies') }} v
JOIN {{ ref('stg_employers') }} e ON e.employer_id = v.employer_id
GROUP BY e.name
ORDER BY n_vacancies DESC
LIMIT 20
