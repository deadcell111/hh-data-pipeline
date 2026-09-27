SELECT DISTINCT jsonb_array_elements(payload->'key_skills')->>'name' AS skill_name
FROM {{ source('raw', 'hh_vacancies_raw') }}
WHERE payload->'key_skills' IS NOT NULL
AND jsonb_array_length(payload->'key_skills') > 0