import json, os, re, sys
import requests
from google_play_scraper import app

DEV_URL = "https://play.google.com/store/apps/dev?id=7457413081606165342&hl=id&gl=id"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}

ids = set()

# 1) Scrape halaman developer
try:
    r = requests.get(DEV_URL, headers=HEADERS, cookies={"CONSENT": "YES+"}, timeout=30)
    found = re.findall(r'details\?id(?:=|\\u003d)([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+)', r.text)
    ids.update(found)
    print(f"Scrape developer: {len(set(found))} ID")
except Exception as e:
    print(f"Scrape developer gagal: {e}")

# 2) Daftar manual (opsional)
if os.path.exists("app_ids.txt"):
    with open("app_ids.txt", encoding="utf-8") as f:
        manual = {l.strip() for l in f if l.strip() and not l.startswith("#")}
    ids.update(manual)
    print(f"app_ids.txt: {len(manual)} ID")

# 3) ID dari apps.json lama + simpan data lama sebagai cadangan
old = {}
if os.path.exists("apps.json"):
    try:
        with open("apps.json", encoding="utf-8") as f:
            old = {a["appId"]: a for a in json.load(f)}
        ids.update(old.keys())
    except Exception as e:
        print(f"apps.json lama tidak terbaca: {e}")

if not ids:
    print("Tidak ada ID sama sekali, apps.json TIDAK diubah.")
    sys.exit(1)

apps = []
for aid in sorted(ids):
    try:
        d = app(aid, lang="id", country="id")
        apps.append({
            "appId": d.get("appId"),
            "title": d.get("title"),
            "icon": d.get("icon"),
            "summary": d.get("summary"),
            "scoreText": d.get("scoreText"),
            "installs": d.get("installs"),
            "url": f"https://play.google.com/store/apps/details?id={d.get('appId')}",
        })
    except Exception as err:
        print(f"Gagal detail {aid}: {err}")
        if aid in old:
            apps.append(old[aid])  # pakai data lama, jangan hilang

if not apps:
    print("Hasil kosong, apps.json TIDAK diubah.")
    sys.exit(1)

with open("apps.json", "w", encoding="utf-8") as f:
    json.dump(apps, f, ensure_ascii=False, indent=4)
print(f"Berhasil: {len(apps)} aplikasi.")
