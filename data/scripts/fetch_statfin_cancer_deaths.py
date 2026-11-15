"""Fetch Statistics Finland StatFin table 13u5 (deaths & crude mortality rate per 100 000 by underlying cause, by wellbeing services county)
for cancers (04-21), colon (07), rectum/anus (08), lung (11), breast (13), pancreas (10); years 2019-2025. NOTE: crude rates, NOT age-standardised."""
import json, urllib.request, csv, os
D=os.path.join(os.path.dirname(__file__),'..')
URL="https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/ksyyt/13u5.px"
q={"query":[{"code":"alue_23_20260101","selection":{"filter":"all","values":["*"]}},
 {"code":"kuolinsyyt_1_20210101","selection":{"filter":"item","values":["04-21","07","08","10","11","13"]}},
 {"code":"timeperiod_y","selection":{"filter":"item","values":[str(y) for y in range(2019,2026)]}},
 {"code":"contentscode","selection":{"filter":"item","values":["ksyylkm","ksyycdr"]}}],"response":{"format":"json-stat2"}}
req=urllib.request.Request(URL,data=json.dumps(q).encode(),headers={'Content-Type':'application/json'})
js=json.load(urllib.request.urlopen(req,timeout=120)); json.dump(js,open(f'{D}/raw/statfin_13u5_cancer_deaths.json','w'),ensure_ascii=False)
dims=js['id']; sizes=js['size']; cats=[js['dimension'][d]['category'] for d in dims]
import itertools
keys=[sorted(c['index'],key=lambda k:c['index'][k]) for c in cats]
rows={}
for n,combo in enumerate(itertools.product(*keys)):
    v=js['value'][n]; a,c,y,m=combo
    k=(a,c,y); r=rows.setdefault(k,dict(region=cats[0]['label'][a],region_code=a,year=y,cause=cats[1]['label'][c],cause_code=c))
    r['deaths' if m=='ksyylkm' else 'crude_rate_per_100000']=v
out=[]
for r in rows.values():
    out.append(dict(region=r['region'],region_code=r['region_code'],year=r['year'],sex='total',indicator='Deaths by underlying cause: '+r['cause'],
      value=r.get('crude_rate_per_100000'),unit='crude deaths per 100 000 population (NOT age-standardised)',deaths=r.get('deaths'),
      source_url='https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/ksyyt/13u5.px',source_table='Statistics Finland StatFin 13u5 (Kuolleet ja yleinen kuolleisuusluku tilaston peruskuolemansyyn mukaan hyvinvointialueittain)'))
with open(f'{D}/csv/statfin_13u5_cancer_deaths_by_wsc.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(out))
