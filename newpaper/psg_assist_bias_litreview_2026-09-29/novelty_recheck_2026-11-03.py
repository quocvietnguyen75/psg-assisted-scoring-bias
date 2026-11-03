"""Pre-submission novelty re-check for the PSG assisted-scoring paper, via the OpenAlex API (no key, no e-mail sent).

Usage: python novelty_recheck.py <out.json>
1. Forward citations of the seed works, newest first.
2. Topic searches restricted to works published from 2026-01-01.
Prints a compact listing and writes every query with its raw hits to <out.json> as the query log.
"""
import json
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.openalex.org"
HEADERS = {"User-Agent": "psg-novelty-recheck/1.0 (research script)"}
SEEDS = {
    "alvarezestevez2022 (PSG-IPA study, PLOS ONE)": "10.1371/journal.pone.0275530",
    "alvarezestevez2019 (arousal detector, reviewed output in the reference)": "10.1016/j.sleep.2019.01.025",
    "holm2026 (World of ScoreCraft, JSR)": "10.1111/jsr.70113",
    "psgipa (PhysioNet dataset)": "10.13026/esx0-nw71",
}
SEARCHES = [
    "assisted scoring polysomnography reference standard",
    "semi-automatic scoring polysomnography agreement",
    "automatic sleep staging validation reference standard bias",
    "incorporation bias sleep scoring",
    "anchoring automation bias sleep staging",
    "pre-scoring polysomnography technologists edit automatic scoring",
    "PSG-IPA",
    "human-in-the-loop sleep scoring reference",
]
log = {"run": time.strftime("%Y-%m-%d %H:%M"), "queries": []}


def get(url: str):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def short(w):
    venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "?"
    return f"{w.get('publication_date')} | {w.get('title')} | {venue} | {w.get('doi')}"


print("=== 1. Forward citations (newest first) ===")
for name, doi in SEEDS.items():
    if not doi:
        print(f"\n--- {name}: no DOI resolved")
        continue
    try:
        w = get(f"{API}/works/doi:{urllib.parse.quote(doi)}")
    except Exception as e:  # noqa: BLE001
        print(f"\n--- {name} ({doi}): not found in OpenAlex ({e})")
        log["queries"].append({"seed": name, "doi": doi, "error": str(e)})
        continue
    wid = w["id"].rsplit("/", 1)[-1]
    cites = get(f"{API}/works?filter=cites:{wid}&sort=publication_date:desc&per-page=50")
    hits = cites["results"]
    print(f"\n--- {name} ({doi}): cited by {w.get('cited_by_count')} in OpenAlex; newest {min(len(hits), 50)}:")
    for h in hits:
        if (h.get("publication_date") or "") >= "2025-09-01":
            print("   ", short(h))
    log["queries"].append({"seed": name, "doi": doi, "openalex": wid, "cited_by_count": w.get("cited_by_count"),
                           "citing_newest": [short(h) for h in hits]})
    time.sleep(0.3)

print("\n=== 2. Topic searches, works from 2026-01-01 ===")
for q in SEARCHES:
    url = (f"{API}/works?search={urllib.parse.quote(q)}&filter=from_publication_date:2026-01-01"
           f"&per-page=12")
    try:
        r = get(url)
    except Exception as e:  # noqa: BLE001
        print(f"\n--- '{q}': failed ({e})")
        continue
    print(f"\n--- '{q}': {r['meta']['count']} works since 2026-01-01; top {len(r['results'])} by relevance:")
    for h in r["results"]:
        print("   ", short(h))
    log["queries"].append({"search": q, "filter": "from_publication_date:2026-01-01", "count": r["meta"]["count"],
                           "top": [short(h) for h in r["results"]]})
    time.sleep(0.3)

json.dump(log, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\nquery log written:", sys.argv[1])
