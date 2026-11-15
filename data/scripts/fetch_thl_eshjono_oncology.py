"""THL 'Hoitoa ja hoidon tarpeen arviointia odottavat erikoisaloittain' cube (sampo.thl.fi eshjono/jonotilanne),
specialty 65 Syöpätaudit (oncology, sid 862186), by wellbeing services county (producer), selected month-end dates.
Data are UNVERIFIED monthly figures (THL note), producer-based (not residence), only non-urgent care."""
import json, urllib.request, csv, os, sys
D=os.path.join(os.path.dirname(__file__),'..')
BASE="https://sampo.thl.fi/pivot/prod/fi/eshjono/jonotilanne/fact_eshjono_jonotilanne"
s=open(f'{D}/raw/thl_eshjono_dims.json').read() if os.path.exists(f'{D}/raw/thl_eshjono_dims.json') else urllib.request.urlopen(BASE+'.dimensions.json').read().decode()
dims=json.JSONDecoder().raw_decode(s[s.index('(')+1:].strip())[0]
times=[x for x in dims if x['id']=='ajankohta'][0]['children'][0]['children']
regs=[x for x in dims if x['id']=='tuottaja'][0]['children'][0]
pick=[t for t in times if t['label'] in ('31.12.2023','31.12.2024','31.12.2025','30.09.2026')]
MEAS={'738214':'Waiting for treatment (n)','738219':'Waiting for treatment >90 d (n)','738220':'Waiting for treatment >90 d (%)','738217':'Waiting for treatment >180 d (%)',
      '738222':'Waiting for assessment of need for treatment (n)','738228':'Waiting for assessment >90 d (%)'}
rows=[]
for t in pick:
    url=f"{BASE}.json?row=tuottaja-{'.'.join([str(regs['sid'])]+[str(c['sid']) for c in regs['children']])}&column=measure-{'.'.join(MEAS)}&filter=erikoisala-862186&filter=ajankohta-{t['sid']}"
    js=json.load(urllib.request.urlopen(url,timeout=120))
    json.dump(js,open(f"{D}/raw/thl_eshjono_oncology_{t['label']}.json","w"),ensure_ascii=False)
    ds=js['dataset']; ids=ds['dimension']['id']
    rcat=ds['dimension']['tuottaja']['category']; mcat=ds['dimension']['measure']['category']
    rk=sorted(rcat['index'],key=lambda k:rcat['index'][k]); mk=sorted(mcat['index'],key=lambda k:mcat['index'][k])
    vals=ds['value']
    for i,r in enumerate(rk):
        for j,m in enumerate(mk):
            idx=str(i*len(mk)+j); v=vals.get(idx) if isinstance(vals,dict) else vals[int(idx)]
            if v in (None,'..',''): continue
            rows.append(dict(region=rcat['label'][r],region_code=f'THL-tuottaja-{r}',year=t['label'],sex='total',indicator='Oncology (specialty 65 Syöpätaudit), non-urgent: '+mcat['label'][m],
              value=v,unit='% or count',source_url=BASE.replace('/fact_eshjono_jonotilanne','')+'/summary_hvaraportti',source_table=f'THL eshjono/jonotilanne cube, erikoisala 65 Syöpätaudit, measure {m} ({MEAS.get(m,"")}), ajankohta {t["label"]}; API {url}'))
with open(f'{D}/csv/thl_eshjono_oncology_waits_by_wsc.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows))
