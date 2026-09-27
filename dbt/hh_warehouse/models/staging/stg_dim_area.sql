SELECT DISTINCT
    payload->'area'->>'id' AS area_id,
    payload->'area'->>'name' AS name
FROM {{ source('raw', 'hh_vacancies_raw') }}
WHERE payload->'area'->>'id' IS NOT NULL