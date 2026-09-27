SELECT DISTINCT
    payload->'experience'->>'id' AS experience_id,
    payload->'experience'->>'name' AS experience_name
FROM {{source ('raw', 'hh_vacancies_raw') }}
WHERE payload->'experience'->>'id' IS NOT NULL