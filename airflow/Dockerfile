FROM apache/airflow:2.10.2

# requests/python-dotenv/psycopg2-binary run in Airflow's own Python env,
# since fetch.py / load_raw.py are invoked as `python3 <script>` from the DAG.
RUN pip install --no-cache-dir \
    requests \
    python-dotenv \
    psycopg2-binary

# dbt-postgres pulls in a newer click than celery (Airflow's worker CLI)
# tolerates, breaking the worker on startup if installed into the same
# environment. Isolate it in its own venv instead.
RUN python3 -m venv /home/airflow/dbt_venv && \
    /home/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-postgres
