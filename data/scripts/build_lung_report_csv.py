"""Parse Taulukko 11 (treatment modality & MDT by wellbeing services county, lung cancer 2019-2023)
and Taulukko 4 (stage information coverage) from the Finnish Cancer Registry / FICAN lung cancer report (published 23.4.2026):
https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html  (raw copy: raw/keuhkosyoparaportti_2026.html)"""
import pandas as pd, io, os, csv, json
D=os.path.join(os.path.dirname(__file__),'..')
URL='https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html'
ts=pd.read_html(io.StringIO(open(f'{D}/raw/keuhkosyoparaportti_2026.html',encoding='utf-8',errors='ignore').read()))
t=ts[10].copy(); t['Hoitomuoto']=t['Hoitomuoto'].ffill(); t['Yhteistyöalue']=t['Yhteistyöalue'].ffill()
t=t[pd.to_numeric(t['Osuus (%)'],errors='coerce').notna()]
codes={r['title']['fi']:r['code'] for r in json.load(open(f'{D}/raw/sotkanet_regions.json')) if r['category']=='HYVINVOINTIALUE'}
en={r['title']['fi']:r['title']['en'] for r in json.load(open(f'{D}/raw/sotkanet_regions.json')) if r['category']=='HYVINVOINTIALUE'}
EN={'Parantava':'curative treatment','Jarruttava':'life-prolonging (non-curative) treatment','Oireenmukainen':'symptomatic/palliative treatment','Ei hoitotietoa':'no treatment record','MDT-käsittely':'MDT meeting recorded'}
rows=[]
for _,r in t.iterrows():
    hva=str(r['Hyvinvointialue'])
    if hva in ('nan','Yhteistyöalue yhteensä') : continue
    rows.append(dict(region=en.get(hva,hva),region_name_fi=hva,region_code=codes.get(hva,''),region_type='HYVINVOINTIALUE' if hva in codes else 'OTHER',
      year='2019-2023 (diagnosis years; 12-month follow-up)',sex='total',indicator=f"Lung cancer (C33-C34) patients with {EN.get(r['Hoitomuoto'],r['Hoitomuoto'])} within 12 months, % (crude)",
      treatment_group_fi=r['Hoitomuoto'],collaborative_area_fi=r['Yhteistyöalue'],value=float(r['Osuus (%)']),numerator=int(r['Lukumäärä']),denominator=int(r['Yhteensä']),unit='%',
      source_url=URL,source_table='Keuhkosyöpä Suomessa 2019-2023 (Finnish Cancer Registry/THL/FICAN, publ. 23.4.2026), Taulukko 11'))
with open(f'{D}/csv/lung_report2026_treatment_by_wsc.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
s=ts[3]; s.columns=['stage_info_type_fi','n','pct']
s['source_url']=URL; s['source_table']='Keuhkosyöpä Suomessa 2019-2023, Taulukko 4 (whole country, N=14873)'
s.to_csv(f'{D}/csv/lung_report2026_stage_info_coverage_national.csv',index=False)
print(len(rows))
for g in ['Parantava','Ei hoitotietoa','MDT-käsittely']:
    L=sorted([r for r in rows if r['treatment_group_fi']==g],key=lambda r:r['value'])
    print(g,[(r['region_name_fi'][:14],r['value'],r['denominator']) for r in L])

# ---- Taulukko 10 (same groups by collaborative area, YTA) + Wilson CIs computed by us
import math
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return round(100*(c-h),1),round(100*(c+h),1)
t10=ts[9].copy(); t10['Hoitomuoto']=t10['Hoitomuoto'].ffill(); t10=t10[pd.to_numeric(t10['Osuus (%)'],errors='coerce').notna()]
YC={'Etelä-Suomen yhteistyöalue':'YTA-ETELA','Itä-Suomen yhteistyöalue':'YTA-ITA','Länsi-Suomen yhteistyöalue':'YTA-LANSI','Pohjois-Suomen yhteistyöalue':'YTA-POHJOIS','Sisä-Suomen yhteistyöalue':'YTA-SISA','Koko maa':'358'}
r10=[]
for _,r in t10.iterrows():
    k,n=int(r['Lukumäärä']),int(r['Yhteensä']); lo,hi=wilson(k,n); y=r['Yhteistyöalue']
    r10.append(dict(region={'Etelä-Suomen yhteistyöalue':'South Finland collaborative area (YTA)','Itä-Suomen yhteistyöalue':'East Finland collaborative area (YTA)','Länsi-Suomen yhteistyöalue':'West Finland collaborative area (YTA)','Pohjois-Suomen yhteistyöalue':'North Finland collaborative area (YTA)','Sisä-Suomen yhteistyöalue':'Inland Finland collaborative area (YTA)'}.get(y,'Finland'),region_name_fi=y,region_code=YC.get(y,''),region_type='YTA' if y!='Koko maa' else 'MAA',
      year='2019-2023 (diagnosis years; 12-month follow-up)',sex='total',indicator=f"Lung cancer (C33-C34) patients with {EN.get(r['Hoitomuoto'],r['Hoitomuoto'])} within 12 months, % (crude)",
      treatment_group_fi=r['Hoitomuoto'],value=float(r['Osuus (%)']),numerator=k,denominator=n,unit='%',ci95_low=lo,ci95_high=hi,ci_method='Wilson 95% CI computed by us from n/N',
      source_url=URL,source_table='Keuhkosyöpä Suomessa 2019-2023 (Finnish Cancer Registry/THL/FICAN, publ. 23.4.2026), Taulukko 10'))
with open(f'{D}/csv/lung_report2026_treatment_by_yta.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(r10[0].keys())); w.writeheader(); w.writerows(r10)
print('Taulukko 10 rows',len(r10))

# ---- Taulukko 5 (pandas table index 4): national patients per follow-up start year, with visit / procedure / MDT / death counts
t5=ts[4].copy(); t5.columns=['year','patients','visit_n','visit_pct','procedure_n','procedure_pct','mdt_n','mdt_pct','death_n','death_pct']
r5=[]
for _,r in t5.iterrows():
    if str(r['year'])=='Yhteensä': continue
    for key,lab in [('patients','New lung cancer patients (C33-C34), by year of follow-up start'),('procedure','Patients with a lung cancer treatment procedure recorded within 12 months'),('mdt','Patients with an MDT meeting recorded within 12 months'),('death','Patients who died within 12 months')]:
        r5.append(dict(region='Finland',region_code='358',year=int(r['year']),indicator=lab,value=int(r[key] if key=='patients' else r[key+'_n']),
            pct=('' if key=='patients' else float(r[key+'_pct'])),unit='patients',source_url=URL,source_table='Keuhkosyöpä Suomessa 2019-2023 (publ. 23.4.2026), Taulukko 5 (by year of follow-up start)'))
with open(f'{D}/csv/lung_report2026_national_by_year.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(r5[0].keys())); w.writeheader(); w.writerows(r5)
print('national by year rows',len(r5))
