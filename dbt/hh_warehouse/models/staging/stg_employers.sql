SELECT DISTINCT
    payload->'employer'->>'id'   AS employer_id,
    payload->'employer'->>'name' AS name,
    payload->'employer'->>'url'  AS url
FROM {{ source('raw', 'hh_vacancies_raw') }}
WHERE payload->'employer'->>'id' IS NOT NULL
