SELECT DISTINCT
    r.role->>'id' AS role_id,
    r.role->>'name' AS role_name
FROM {{ source('raw', 'hh_vacancies_raw') }} v
CROSS JOIN LATERAL jsonb_array_elements(v.payload->'professional_roles') AS r(role)