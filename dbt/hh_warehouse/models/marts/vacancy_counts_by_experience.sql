SELECT
    x.experience_name AS experience,
    count(*)          AS n_vacancies
FROM {{ ref('stg_dim_vacancies') }} v
JOIN {{ ref('stg_dim_experience') }} x ON x.experience_id = v.experience_id
GROUP BY x.experience_name
ORDER BY n_vacancies DESC
