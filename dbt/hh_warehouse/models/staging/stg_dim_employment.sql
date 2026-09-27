SELECT DISTINCT
    payload->'employment_form'->>'id' AS employment_form_id,
    payload->'employment_form'->>'name' AS employment_form_name
FROM {{ source('raw', 'hh_vacancies_raw') }}
WHERE payload->'employment_form'->>'id' IS NOT NULL