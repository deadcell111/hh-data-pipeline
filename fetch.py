import requests
import json 
from pathlib import Path
import datetime as dt 
import time
from dotenv import load_dotenv
import os

load_dotenv()


USER_AGENT = os.environ.get("HH_USER_AGENT", "kz-job-market/0.1 (talgatkozahmetov4@gmail.com)")

BASE = "https://api.hh.ru"
QUERIES = ["Python"]
TOKEN = os.environ.get("HH_TOKEN")
AREA = 160 
PER_PAGE = 100
MAX_PAGES = 20 
WINDOW_DAYS = int(os.environ.get("HH_WINDOW_DAYS", "1"))

ROOT = Path('data/raw')
SLEEP = 0.3
RETRIES = 3 

if not TOKEN:
    raise SystemExit("there is no HH_TOKEN.")

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT,
                        "Authorization":f"Bearer {TOKEN}",})

class FetchError(Exception):
    """catches error"""

def get(url: str, params: dict | None = None) -> dict: #get function that retries 3 times
    last_error = None
    for attempt in range(RETRIES):
        try:
            r = session.get(url, params=params, timeout=30) #gets http responses
        except Exception as e:
            last_error = f"network: {e}"
            time.sleep(2 ** attempt)
            continue

        if r.status_code == 200:
            return r.json()

        body = r.text[:300]

        if r.status_code in (401,403):
            raise FetchError(f"{r.status_code} {url} params={params} body={body}")

        if r.status_code == 429:
            time.sleep(5 * (attempt + 1))
            last_error = f"429 rate limit: {body}"
            time.sleep(2 ** attempt)

    raise RuntimeError(f"failed after {RETRIES} attempts: {url} {params} -> {last_error}")

def saveJson(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False  ), encoding="utf-8") #Nothing returns, makes directory with existinfg parents to save json file from fetcher

def slug(text: str) -> str:
    return text.replace(" ", "_") 

def fetch_lists(today: str, stats: dict) -> set[str]:
    seen_today: set[str] = set() 
    date_to = dt.date.fromisoformat(today)
    date_from = date_to - dt.timedelta(days=WINDOW_DAYS)

    for query in QUERIES:
        for page in range(MAX_PAGES):
            out = ROOT / "vacancies_list" / f"dt={today}" / f"q={slug(query)}" / f"page={page:02d}.json"

            if out.exists():
                seen_today.update(
                    item['id'] for item in json.loads(out.read_text(encoding="utf-8"))["items"] #updates previous page if that page is exists
                )
                continue

            params = {
                "text": query,
                "area": AREA,
                "per_page": PER_PAGE,
                "page": page,
                "date_from": date_from.isoformat(),
                "date_to": date_to.isoformat(),
            } #default params
            try:
                data = get(f"{BASE}/vacancies", params) #get vacancies by BASE url and parametrs 
            except RuntimeError as e:
                stats["errors"].append(str(e))
                break

            items = data.get("items", [])
            if not items:
                break 

            saveJson(out, data)
            seen_today.update(item["id"] for item in items)
            stats["pages"] += 1
            stats["items"] += len(items)

            if page == 0 and data.get("found", 0) > PER_PAGE * MAX_PAGES:
                stats["truncated"].append({"query": query, "found": data["found"]})

            if page + 1 >= data.get("pages", 0):
                break

            time.sleep(SLEEP)

    return seen_today


def fetch_details(vacancy_ids: set[str], stats: dict) -> None:
    #details per vacancy, description and key_skills
    details_dir = ROOT / "vacancy_detail"
    details_dir.mkdir(parents=True, exist_ok=True)

    for vid in sorted(vacancy_ids):
        out = details_dir / f"id={vid}.json"
        if out.exists():
            continue
        try:
            saveJson(out, get(f"{BASE}/vacancies/{vid}"))
            stats["details"] += 1
        except FetchError as e:
            stats["errors"].append(str(e))
        time.sleep(SLEEP)

def fetch_reference(today: str, stats: dict) -> None:
    for name in ("areas","professional_roles"):
        out = ROOT / "reference" / f"dt={today}" / f"{name}.json"

        if out.exists():
            continue
        try:
            saveJson(out, {"data": get(f"{BASE}/{name}")})
        except FetchError as e:
            stats["errors"].append(str(e))

def main() -> None:
    today = dt.date.today().isoformat()
    started = time.time()
    stats = {"pages": 0, "items": 0, "details": 0, "errors": [], "truncated": []}

    fetch_reference(today, stats)
    ids = fetch_lists(today, stats)
    fetch_details(ids, stats)

    manifest = {
        "date": today,
        "started_at": dt.datetime.fromtimestamp(started).isoformat(timespec="seconds"),
        "duration_sec": round(time.time() - started, 1),
        "queries": QUERIES,
        "area": AREA,
        "unique_ids": len(ids),
        **stats,
    }
    saveJson(ROOT / "_manifests" / f"{today}.json", manifest)
 
    print(json.dumps(
        {k: v for k, v in manifest.items() if k not in ("errors", "queries")},
        ensure_ascii=False,
    ))
    for err in stats["errors"]:            
        print("ERROR:", err)
    for t in stats["truncated"]:
        print(f"request: '{t['query']}' found {t['found']} "
              f"{PER_PAGE * MAX_PAGES}")
if __name__ == "__main__":
    main()