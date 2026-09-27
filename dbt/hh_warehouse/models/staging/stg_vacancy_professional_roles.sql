SELECT DISTINCT
    v.payload->>'id' AS vacancy_id,
    r.role->>'id'    AS role_id
FROM {{ source('raw', 'hh_vacancies_raw') }} v
CROSS JOIN LATERAL jsonb_array_elements(v.payload->'professional_roles') AS r(role)
