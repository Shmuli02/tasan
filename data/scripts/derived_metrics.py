"""Derived metrics computed ONLY from fetched data:
1) Colorectal screening shortfall vs strategy target (80% in every wellbeing services county): implied invitees = abs_value/value*100,
   extra attendees needed = 0.8*invitees - abs_value. ASSUMPTION: Sotkanet abs_value for indicator 6103 = number who attended (numerator).
2) Wilson 95% CIs for lung-cancer curative-treatment share by county (Taulukko 11)."""
import csv, math, os
D=os.path.join(os.path.dirname(__file__),'..')
rows=list(csv.DictReader(open(f'{D}/csv/sotkanet_6103_screening_colorectal_attendance.csv')))
out=[]
for r in rows:
    if r['region_code']=='91' or not r['abs_value']: continue
    v=float(r['value']); a=float(r['abs_value']); inv=a/v*100
    out.append(dict(region=r['region'],region_name_fi=r['region_name_fi'],region_code=r['region_code'],year=r['year'],sex=r['sex'],
      indicator='Colorectal screening: attendance %, gap to 80% target, extra attendees needed',value=v,attended_abs=int(a),implied_invited=round(inv),
      gap_to_80_pp=round(80-v,1),extra_attendees_needed_for_80=max(0,round(0.8*inv-a)),unit='% / persons',
      source_url=r['source_url'],source_table=r['source_table']+' | derived: scripts/derived_metrics.py'))
with open(f'{D}/csv/derived_colorectal_screening_gap_to_target.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
for s in ['total','male','female']:
    nat=[o for o in out if o['year']=='2024' and o['sex']==s and o['region_code']=='358'][0]
    reg=sum(o['extra_attendees_needed_for_80'] for o in out if o['year']=='2024' and o['sex']==s and o['region_code']!='358')
    print('2024',s,'nat',nat['value'],'invited~',nat['implied_invited'],'attended',nat['attended_abs'],'extra needed (national)',nat['extra_attendees_needed_for_80'],'sum over regions',reg)
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return round(100*(c-h),1),round(100*(c+h),1)
L=list(csv.DictReader(open(f'{D}/csv/lung_report2026_treatment_by_wsc.csv')))
o2=[]
for r in L:
    lo,hi=wilson(int(r['numerator']),int(r['denominator'])); r=dict(r); r['ci95_low']=lo; r['ci95_high']=hi; o2.append(r)
with open(f'{D}/csv/lung_report2026_treatment_by_wsc.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(o2[0].keys())); w.writeheader(); w.writerows(o2)
for r in sorted([r for r in o2 if r['treatment_group_fi']=='Parantava'],key=lambda r:float(r['value'])):
    print(r['region_name_fi'][:30],r['value'],r['ci95_low'],r['ci95_high'],r['numerator'],'/',r['denominator'])
