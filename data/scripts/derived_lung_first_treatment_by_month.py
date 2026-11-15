"""DERIVED (by us) from Keuhkosyöpä Suomessa 2024, Taulukko 4.5 (PDF p.34): cumulative share of ALL lung cancer patients whose FIRST event
by month m after diagnosis was an active anticancer treatment = surgery + non-palliative radiotherapy + systemic drug therapy (first events are
mutually exclusive, so the columns add). Denominator for the approximate Wilson CI = YTA patient total printed in Taulukko 3.3 (PDF p.18);
the cumulative shares are printed without n, so CIs are APPROXIMATE."""
import csv, os, math
D=os.path.join(os.path.dirname(__file__),'..')
def wilson(p,n,z=1.96):
    d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return round(100*(c-h),1),round(100*(c+h),1)
N={'Etelä-Suomi':4972,'Itä-Suomi':2019,'Länsi-Suomi':2284,'Pohjois-Suomi':1930,'Sisä-Suomi':2033}
L=list(csv.DictReader(open(f'{D}/csv/lung_report2024_first_event_cumulative_by_yta.csv')))
acc={}
for r in L:
    if r['event_fi'] in ('Leikkaushoito','Muu kuin palliatiivinen sädehoito','Lääkehoito'):
        k=(r['region_name_fi'],int(r['month'])); acc.setdefault(k,[r,0.0]); acc[k][1]+=float(r['value'])
out=[]
for (y,m),(r,v) in sorted(acc.items()):
    if m==0: continue
    lo,hi=wilson(v/100,N[y])
    out.append(dict(region=r['region'],region_name_fi=y,region_code=r['region_code'],region_type='YTA',year='diagnosed 1/2018-6/2022',sex='total',month=m,
      indicator=f'Share of ALL lung cancer patients whose first active treatment (surgery, non-palliative RT or systemic drug therapy) started within {m} month(s) of diagnosis, % (DERIVED: sum of Taulukko 4.5 first-event columns)',
      value=round(v,1),unit='%',ci95_low=lo,ci95_high=hi,ci_method=f'approximate Wilson 95% CI computed by us, denominator = YTA total in Taulukko 3.3 (n={N[y]})',denominator=N[y],
      source_url='https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf',source_table='Keuhkosyöpä Suomessa (2024), Taulukko 4.5 PDF p.34 + Taulukko 3.3 PDF p.18; derived by us'))
with open(f'{D}/csv/lung_derived_first_active_treatment_by_month_yta.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for r in out:
    if r['month'] in (1,2,6): print(r['month'],r['region_name_fi'],r['value'],r['ci95_low'],r['ci95_high'])
