import json
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

ROOT = Path("data/raw")

UPSERT_SQL = """
    INSERT INTO raw.hh_vacancies_raw (id, payload)
    VALUES (%s, %s)
    ON CONFLICT (id) DO UPDATE
    SET payload = EXCLUDED.payload,
        loaded_at = now()
"""


def load_detail_files(conn) -> dict:
    stats = {"loaded": 0, "errors": []}
    files = sorted(ROOT.glob("vacancy_detail/id=*.json"))

    with conn.cursor() as cur:
        for path in files:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                vacancy_id = payload["id"]
            except Exception as e:
                stats["errors"].append(f"{path.name}: {e}")
                continue

            cur.execute(UPSERT_SQL, [vacancy_id, psycopg2.extras.Json(payload)])
            stats["loaded"] += 1

    conn.commit()
    return stats


def main() -> None:
    conn = psycopg2.connect()  
    try:
        stats = load_detail_files(conn)
    finally:
        conn.close()

    print(json.dumps(stats, ensure_ascii=False))
    for err in stats["errors"]:
        print("ERROR:", err)


if __name__ == "__main__":
    main()
