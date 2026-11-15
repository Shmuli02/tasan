"""Compute spreads (min, max, max/min ratio, max-min gap, ranks) across wellbeing services counties for each indicator & year.
Excludes Helsinki (code 90, not a wellbeing county but organiser) only where flagged; Åland (91) excluded (separate system)."""
import json, csv, collections, os
D=os.path.join(os.path.dirname(__file__),'..')
rows=json.load(open(f'{D}/raw/sotkanet_all_tidy.json'))
g=collections.defaultdict(list)
for r in rows:
    if r['region_type']=='HYVINVOINTIALUE' and r['region_code']!='91': g[(r['indicator_id'],r['indicator'],r['year'],r['sex'])].append(r)
nat={(r['indicator_id'],r['year'],r['sex']):r['value'] for r in rows if r['region_type']=='MAA'}
out=[]
for (i,ind,y,s),L in sorted(g.items()):
    L=sorted(L,key=lambda r:r['value'])
    lo,hi=L[0],L[-1]
    out.append(dict(indicator_id=i,indicator=ind,year=y,sex=s,n_regions=len(L),national=nat.get((i,y,s),''),
      min_region=lo['region'],min_value=lo['value'],max_region=hi['region'],max_value=hi['value'],
      gap_abs=round(hi['value']-lo['value'],2),ratio_max_min=round(hi['value']/lo['value'],3) if lo['value'] else '',
      ranking_low_to_high=' | '.join(f"{r['region_code']}:{r['value']}" for r in L),source_url=lo['source_url']))
with open(f'{D}/csv/spreads_by_indicator_year.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
