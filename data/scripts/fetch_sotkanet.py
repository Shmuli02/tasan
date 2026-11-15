"""Fetch selected THL Sotkanet indicators (REST API 1.1) for all regions, years 2010-2025.
Raw JSON saved to data/raw/sotkanet/<id>.json and metadata to <id>_meta.json.
Usage: python3 scripts/fetch_sotkanet.py"""
import json, os, urllib.request, time
BASE="https://sotkanet.fi/rest/1.1"
IDS=[3620,3621,6103,3625,3626,3627,5643,5644,245,10024,5093,5395,13,5033,5073,3336,5083,6411,6410,2676,3175,186]
OUT=os.path.join(os.path.dirname(__file__),'..','raw','sotkanet'); os.makedirs(OUT,exist_ok=True)
def get(url):
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'curl/8.5.0 (junction-new research)'}),timeout=120) as r: return json.load(r)
        except Exception as e: print('retry',url,e); time.sleep(3)
    raise SystemExit('failed '+url)
for i in IDS:
    meta=get(f"{BASE}/indicators/{i}?lang=en"); json.dump(meta,open(f"{OUT}/{i}_meta.json","w"),ensure_ascii=False)
    yrs="&".join(f"years={y}" for y in range(2010,2026))
    data=get(f"{BASE}/json?indicator={i}&{yrs}&genders=total&genders=male&genders=female")
    json.dump(data,open(f"{OUT}/{i}.json","w"),ensure_ascii=False)
    print(i,meta['title']['en'][:80],len(data),meta.get('range'))
