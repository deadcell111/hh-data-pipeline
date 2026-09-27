SELECT DISTINCT
    v.payload->>'id' AS vacancy_id,
    s.skill_name      AS skill_name
FROM {{ source('raw', 'hh_vacancies_raw') }} v
CROSS JOIN LATERAL jsonb_array_elements(v.payload->'key_skills') AS k(skill)
JOIN {{ ref('stg_dim_skills') }} s ON s.skill_name = k.skill->>'name'
