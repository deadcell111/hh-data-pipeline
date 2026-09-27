SELECT
    payload->>'id' AS vacancy_id,
    payload->>'name' AS title,
    payload->'employer'->>'id' AS employer_id,
    (payload->'salary'->>'from')::numeric AS salary_from,
    (payload->'salary'->>'to')::numeric AS salary_to,
    payload->'salary'->>'currency' AS currency,
    (payload->'salary'->>'gross')::boolean AS gross,
    payload->'area'->>'id' AS area_id,
    payload->'experience'->>'id' AS experience_id,
    payload->'employment_form'->>'id' AS employment_id,
    (payload->>'archived')::BOOLEAN AS archived,
    (payload->>'published_at')::timestamptz AS published_at,
    (payload->>'created_at')::timestamptz AS created_at
FROM {{source ('raw', 'hh_vacancies_raw') }}
