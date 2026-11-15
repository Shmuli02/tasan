"""Regional tables from 'Keuhkosyöpä Suomessa – Katsaus keuhkosyövän hoidon laadusta' (Finnish Cancer Registry/FICAN/THL, Dec 2024),
https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf  (cohort: lung cancers C33-C34 diagnosed 1.1.2018-30.6.2022, N=13 324, excl. Åland).
The PDF tables are vector graphics (no extractable text). Values below were MANUALLY TRANSCRIBED from 200-dpi renders
(raw/lung2024_pages/p-NN.png, pdftoppm -r 200) and then cross-checked automatically against an independent OCR pass
(RapidOCR, scripts/ocr_pages.py -> raw/lung2024_pages/p-NN.ocr.txt) plus internal-consistency checks (count/total = share; 4.5 rows sum to 100; 4.6 == 4.5 month 6).
Page numbers below = PDF page (printed page = PDF page - 1).  Wilson 95% CIs are COMPUTED BY US where only n/N are printed (ci_method column)."""
import csv, os, re, math, json
D=os.path.join(os.path.dirname(__file__),'..')
URL='https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf'
REP='Keuhkosyöpä Suomessa – Katsaus keuhkosyövän hoidon laadusta (Syöpärekisteri/FICAN, 12/2024)'
COH='diagnosed 1/2018-6/2022'
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return round(100*(c-h),1),round(100*(c+h),1)
YTA={'Etelä-Suomi':('South Finland collaborative area (YTA)','YTA-ETELA'),'Itä-Suomi':('East Finland collaborative area (YTA)','YTA-ITA'),
     'Länsi-Suomi':('West Finland collaborative area (YTA)','YTA-LANSI'),'Pohjois-Suomi':('North Finland collaborative area (YTA)','YTA-POHJOIS'),
     'Sisä-Suomi':('Inland Finland collaborative area (YTA)','YTA-SISA'),'Koko maa':('Finland (excl. Åland)','358')}
REG={r['title']['fi']:(r['code'],r['title']['en']) for r in json.load(open(f'{D}/raw/sotkanet_regions.json')) if r['category']=='HYVINVOINTIALUE'}
def hva(gen):
    if gen=='Koko maa': return ('Finland (excl. Åland)','358','MAA')
    k='Helsingin kaupunki' if gen=='Helsingin kaupunki' else gen+' hyvinvointialue'
    c,e=REG[k]; return (e,c,'HYVINVOINTIALUE')
def base(region_fi,region,code,rtype,page,table,sex,ind,val,unit,**kw):
    r=dict(region=region,region_name_fi=region_fi,region_code=code,region_type=rtype,year=kw.pop('year',COH),sex=sex,indicator=ind,value=val,unit=unit,
           ci95_low=kw.pop('lo',''),ci95_high=kw.pop('hi',''),ci_method=kw.pop('cim',''),n=kw.pop('n',''),denominator=kw.pop('den',''),
           source_url=URL,source_table=f'{REP}, {table}, PDF p.{page} (printed p.{page-1})',
           transcription='manual from 200-dpi render; OCR cross-checked',page=page)
    r.update(kw); return r
OUT={}
# ---- Taulukko 3.3 (PDF p.18): treatments within 6 months of diagnosis by YTA (any record; categories overlap)
T33="""Etelä-Suomi|603,1270,868,1079,2329|4972|12.1,25.5,17.5,21.7,46.8
Itä-Suomi|255,439,565,593,929|2019|12.6,21.7,28.0,29.4,46.0
Länsi-Suomi|238,435,365,317,1083|2284|10.4,19.0,16.0,13.9,47.4
Pohjois-Suomi|202,300,455,389,906|1930|10.5,15.5,23.6,20.2,46.9
Sisä-Suomi|324,403,630,437,914|2033|15.9,19.8,31.0,21.5,45.0"""
TR=[('Leikkaushoito','surgery'),('Muu kuin palliatiivinen sädehoito','non-palliative radiotherapy'),('Lääkehoito','systemic drug therapy'),('Palliatiivinen hoito','palliative care'),('Kuollut','died')]
rows=[];chk=[]
for line in T33.splitlines():
    y,ks,N,ps=line.split('|'); N=int(N)
    for (fi,en),k,p in zip(TR,map(int,ks.split(',')),map(float,ps.split(','))):
        lo,hi=wilson(k,N); chk.append(abs(round(100*k/N,1)-p)<=0.051)
        rows.append(base(y,*YTA[y],'YTA',18,'Taulukko 3.3 (= Taulukko 3.4 p.19, same numbers re-ordered)','total',
            f'Lung cancer patients with {en} recorded within 6 months of diagnosis, % (crude; categories not mutually exclusive)',p,'%',lo=lo,hi=hi,cim='Wilson 95% CI computed by us from n/N',n=k,den=N,treatment_fi=fi))
OUT['lung_report2024_treatment_6m_by_yta.csv']=rows
print('3.3 count/total==share checks:',sum(chk),'/',len(chk))
# ---- Taulukko 3.6 (PDF p.23): age-standardised treatment shares by sex & YTA, with printed 95% CI
T36={('Miehet','Leikkaushoito'):"Etelä-Suomi 299 12.2 10.8 14.0;Itä-Suomi 156 13.1 11.0 15.6;Koko maa 881 12.7 11.8 13.7;Länsi-Suomi 125 10.1 8.4 12.1;Pohjois-Suomi 117 11.4 9.4 14.1;Sisä-Suomi 180 16.3 13.9 19.1",
 ('Miehet','Lääkehoito'):"Etelä-Suomi 497 20.8 19.0 23.1;Itä-Suomi 362 30.5 27.3 34.1;Koko maa 1790 25.3 24.1 26.7;Länsi-Suomi 255 19.9 17.5 22.6;Pohjois-Suomi 278 26.6 23.4 30.3;Sisä-Suomi 398 35.4 31.9 39.4",
 ('Miehet','Sädehoito'):"Etelä-Suomi 784 29.9 27.7 32.4;Itä-Suomi 494 37.7 34.2 41.5;Koko maa 2301 30.1 28.8 31.5;Länsi-Suomi 348 26.0 23.2 29.0;Pohjois-Suomi 285 25.2 22.2 28.8;Sisä-Suomi 379 32.0 28.7 35.8",
 ('Naiset','Leikkaushoito'):"Etelä-Suomi 304 16.6 14.8 18.6;Itä-Suomi 99 17.8 14.1 23.4;Koko maa 746 17.3 16.1 18.8;Länsi-Suomi 113 17.1 13.9 21.1;Pohjois-Suomi 85 14.5 11.6 19.3;Sisä-Suomi 144 21.9 18.3 26.4",
 ('Naiset','Lääkehoito'):"Etelä-Suomi 371 20.4 18.3 22.6;Itä-Suomi 203 34.9 30.2 41.4;Koko maa 1093 25.0 23.5 26.7;Länsi-Suomi 110 16.2 13.1 20.1;Pohjois-Suomi 177 30.6 26.0 36.9;Sisä-Suomi 232 35.2 30.6 40.7",
 ('Naiset','Sädehoito'):"Etelä-Suomi 599 28.4 26.0 31.0;Itä-Suomi 198 30.6 26.2 36.6;Koko maa 1358 27.7 26.2 29.4;Länsi-Suomi 182 23.5 19.9 28.1;Pohjois-Suomi 160 26.0 22.0 31.6;Sisä-Suomi 213 28.8 24.8 33.7"}
SEX={'Miehet':'male','Naiset':'female'}; TEN={'Leikkaushoito':'surgery','Lääkehoito':'systemic drug therapy','Sädehoito':'radiotherapy (any)'}
rows=[]
for (s,t),txt in T36.items():
    for it in txt.split(';'):
        *nm,n,v,lo,hi=it.split(); nm=' '.join(nm)
        rows.append(base(nm,*YTA[nm],'YTA' if nm!='Koko maa' else 'MAA',23,'Taulukko 3.6',SEX[s],f'Lung cancer patients treated with {TEN[t]} within 6 months, age-standardised %',float(v),'%',lo=float(lo),hi=float(hi),cim='95% CI as printed in report',n=int(n),treatment_fi=t))
OUT['lung_report2024_treatment_agestd_by_yta_sex.csv']=rows
# ---- Taulukko 3.7 (PDF pp.25-26): same by wellbeing services county
HV=['Etelä-Karjalan','Etelä-Pohjanmaan','Etelä-Savon','Helsingin kaupunki','Itä-Uudenmaan','Kainuun','Kanta-Hämeen','Keski-Pohjanmaan','Keski-Suomen','Keski-Uudenmaan','Koko maa','Kymenlaakson','Lapin','Länsi-Uudenmaan','Pirkanmaan','Pohjanmaan','Pohjois-Karjalan','Pohjois-Pohjanmaan','Pohjois-Savon','Päijät-Hämeen','Satakunnan','Vantaan ja Keravan','Varsinais-Suomen']
T37={('Miehet','Leikkaushoito',25):"30 17.3 11.2 26.4;54 18.2 13.6 24.4;19 7.6 4.5 12.6;83 13.4 10.6 16.8;9 9.2 4.1 18.2;7 5.1 2.0 15.5;28 10.9 7.2 16.5;7 11.5 4.6 25.9;74 23.7 18.4 30.8;29 12.9 8.6 18.6;881 12.6 11.7 13.6;18 6.5 3.8 16.1;30 9.1 6.0 13.7;72 14.2 11.1 18.1;98 17.3 13.9 21.3;22 11.0 6.7 17.5;34 11.9 7.8 18.2;73 14.2 11.1 18.2;29 8.5 5.6 12.9;36 11.1 7.7 16.5;39 10.4 7.3 14.6;22 9.0 5.5 14.1;64 9.7 7.4 12.6",
 ('Miehet','Lääkehoito',25):"23 12.8 7.8 21.0;124 41.1 34.0 49.8;53 22.3 16.5 29.7;155 26.1 22.1 30.7;18 14.5 8.2 24.4;20 16.9 9.8 30.4;69 26.2 20.2 33.9;20 31.2 18.6 50.5;114 36.0 29.3 44.4;9 3.5 1.6 6.9;1790 25.3 24.1 26.6;109 40.5 32.0 54.0;36 10.0 7.0 14.4;47 9.8 7.2 13.2;205 35.9 31.0 41.5;87 38.1 29.9 48.2;58 20.1 14.8 27.4;202 38.6 33.3 44.8;137 38.6 32.3 46.3;128 43.5 35.9 52.8;163 43.7 37.1 51.3;8 3.7 1.6 7.5;5 0.8 0.2 2.0",
 ('Miehet','Sädehoito',25):"25 13.6 8.2 22.3;69 23.8 18.4 30.8;101 40.8 32.9 50.3;186 28.7 24.5 33.4;35 27.6 18.4 40.3;39 31.6 21.2 48.0;77 26.1 19.9 33.9;21 26.6 15.7 44.1;113 32.0 26.0 39.8;80 31.1 24.4 39.1;2301 30.0 28.8 31.4;87 26.1 20.5 37.0;75 21.5 16.6 27.7;153 29.4 24.7 34.8;233 38.7 33.6 44.4;79 32.2 24.8 41.6;75 25.6 19.7 33.4;150 26.6 22.3 31.9;205 50.0 42.9 58.4;131 39.8 32.8 48.6;108 27.4 22.2 33.5;87 32.3 25.5 40.6;161 23.2 19.6 27.3",
 ('Naiset','Leikkaushoito',26):"19 16.9 9.7 28.7;33 25.1 16.8 36.5;20 16.9 10.2 29.0;107 18.6 15.2 23.0;13 16.0 8.1 29.9;6 10.0 3.5 24.6;21 12.4 7.4 20.0;9 32.6 11.3 76.8;36 21.1 14.4 31.1;25 15.0 9.6 22.9;746 17.3 16.0 18.7;17 11.2 6.5 18.1;21 10.4 6.3 16.6;53 17.8 13.0 24.3;90 25.1 19.9 32.2;26 19.8 12.7 30.6;20 15.8 9.4 25.9;49 16.9 12.5 23.4;23 14.9 8.7 26.6;27 12.6 7.8 20.9;26 17.6 11.3 26.3;43 20.5 14.4 29.7;61 15.9 11.9 21.9",
 ('Naiset','Lääkehoito',26):"15 15.4 8.2 27.5;59 45.7 34.4 59.9;44 36.5 26.0 51.9;129 22.9 19.0 27.6;15 19.1 9.8 34.6;11 16.3 7.9 32.1;31 17.1 11.4 25.3;14 39.3 17.5 81.6;61 37.1 27.8 49.7;12 7.3 3.6 13.4;1093 25.0 23.5 26.6;84 49.6 39.3 61.8;27 15.3 9.9 22.9;34 10.5 7.1 15.6;142 39.5 32.9 47.9;48 34.8 24.9 48.3;35 28.0 19.3 40.3;125 42.7 35.3 51.9;63 37.7 28.8 51.2;74 36.9 28.6 48.4;58 39.0 29.3 51.2;8 3.8 1.6 10.0;4 1.0 0.3 4.5",
 ('Naiset','Sädehoito',26):"13 13.8 7.0 25.7;30 19.7 12.8 29.6;37 28.6 19.4 43.0;185 27.3 23.3 32.3;33 25.9 17.0 39.9;17 28.5 16.0 48.6;54 27.0 19.5 36.9;9 27.6 10.7 65.3;49 26.1 18.7 36.9;41 24.4 17.1 34.0;1358 27.6 26.1 29.3;64 29.7 22.3 39.1;43 22.0 15.6 30.5;103 30.0 24.0 37.7;129 32.4 26.6 40.0;45 26.1 18.2 37.4;30 21.2 14.1 31.8;91 28.7 22.8 36.4;82 43.7 34.1 57.8;92 38.9 30.8 50.1;44 27.7 19.8 38.1;68 26.2 20.0 35.4;93 19.9 15.5 26.2"}
rows=[]
for (s,t,pg),txt in T37.items():
    its=txt.split(';'); assert len(its)==23,(s,t,len(its))
    for nm,it in zip(HV,its):
        n,v,lo,hi=it.split(); e,c,rt=hva(nm)
        rows.append(base(nm,e,c,rt,pg,'Taulukko 3.7',SEX[s],f'Lung cancer patients treated with {TEN[t]} within 6 months, age-standardised %',float(v),'%',lo=float(lo),hi=float(hi),cim='95% CI as printed in report',n=int(n),treatment_fi=t,
            caveat='small n (<20): wide CI' if int(n)<20 else ''))
OUT['lung_report2024_treatment_agestd_by_wsc_sex.csv']=rows
# ---- Taulukko 4.1 (PDF p.28): days from diagnosis to first treatment (median, Q1, Q3) by YTA
T41="""Etelä-Suomi|46.0 33.0 63.0|39.0 18.0 56.0|36.0 24.0 54.0
Itä-Suomi|27.0 0.0 43.5|25.0 11.0 47.0|36.0 22.0 56.0
Länsi-Suomi|42.0 28.0 55.0|45.0 26.0 74.5|34.5 23.0 48.2
Pohjois-Suomi|13.5 0.0 44.0|31.0 14.0 54.0|42.0 28.2 57.0
Sisä-Suomi|29.0 0.0 51.0|40.0 21.0 57.8|43.0 28.0 61.0"""
rows=[]
for line in T41.splitlines():
    y,*vals=line.split('|')
    for (fi,en),v in zip([('Leikkaushoito','surgery'),('Sädehoito','radiotherapy'),('Lääkehoito','systemic drug therapy')],vals):
        m,q1,q3=map(float,v.split())
        rows.append(base(y,*YTA[y],'YTA',28,'Taulukko 4.1','total',f'Days from diagnosis to first treatment ({en}), among patients whose first treatment within 6 months was {en}: median',m,'days',
            q1=q1,q3=q3,n='not printed',treatment_fi=fi,caveat=('Q1=0 d: >=25% of surgical patients have surgery recorded on the registry diagnosis date; the report gives no explanation (diagnosis dated from the surgical specimen is OUR plausible interpretation), so low surgical medians partly reflect dating, not only speed. ' if fi=='Leikkaushoito' and q1==0 else '')+'Interval starts at Cancer Registry diagnosis date (not referral); only patients whose FIRST treatment within 6 months was this modality; n per cell not printed.'))
OUT['lung_report2024_days_dx_to_first_treatment_by_yta.csv']=rows
# ---- Taulukko 4.5 (PDF p.34): cumulative % first event 0-6 months by YTA (cols: still no event, surgery, non-pall RT, drug, palliative, died)
T45={'Etelä-Suomi':"100.0 0.0 0.0 0.0 0.0 0.0;59.0 4.8 10.4 5.9 5.0 14.9;37.8 8.1 15.9 8.9 7.3 22.0;28.0 10.0 18.5 10.2 8.3 25.0;22.4 11.1 20.1 10.9 8.8 26.7;18.8 11.6 21.2 11.4 9.1 27.9;16.8 11.8 21.9 11.7 9.3 28.6",
 'Itä-Suomi':"100.0 0.0 0.0 0.0 0.0 0.0;51.8 7.4 9.2 9.7 9.1 12.9;30.8 10.0 13.2 14.8 12.8 18.6;22.1 10.8 14.7 17.2 14.2 20.9;17.3 11.2 15.6 18.8 14.9 22.2;14.0 11.4 16.1 20.0 15.4 23.1;12.1 11.5 16.4 20.8 15.6 23.6",
 'Länsi-Suomi':"100.0 0.0 0.0 0.0 0.0 0.0;65.8 3.7 6.2 6.1 3.5 14.6;43.5 8.2 10.2 9.3 5.9 22.9;33.2 9.8 12.3 10.7 7.2 26.8;27.3 10.1 13.7 11.4 8.2 29.3;22.9 10.1 14.9 11.9 9.0 31.1;20.2 10.2 15.6 12.2 9.6 32.3",
 'Pohjois-Suomi':"100.0 0.0 0.0 0.0 0.0 0.0;58.0 6.5 6.4 7.9 6.6 14.8;37.8 8.5 9.7 12.3 9.7 22.0;28.9 9.1 11.2 14.5 11.1 25.3;23.6 9.3 12.2 15.9 11.9 27.2;19.9 9.4 12.9 16.8 12.5 28.5;17.8 9.5 13.3 17.4 12.8 29.4",
 'Sisä-Suomi':"100.0 0.0 0.0 0.0 0.0 0.0;54.3 8.7 7.1 9.3 6.7 13.9;31.1 12.5 11.0 15.2 10.2 20.0;20.8 13.8 12.8 18.4 11.8 22.5;15.0 14.4 13.8 20.3 12.8 23.7;11.2 14.7 14.5 21.7 13.4 24.5;9.2 14.8 14.9 22.4 13.8 24.9"}
EV=[('Keuhkosyöpä','no first event yet (alive, no treatment record)'),('Leikkaushoito','surgery'),('Muu kuin palliatiivinen sädehoito','non-palliative radiotherapy'),('Lääkehoito','systemic drug therapy'),('Palliatiivinen hoito','palliative care'),('Kuollut','death before any treatment record')]
rows=[];sums=[]
for y,txt in T45.items():
    for m,rw in enumerate(txt.split(';')):
        vals=list(map(float,rw.split())); sums.append(round(sum(vals),1))
        for (fi,en),v in zip(EV,vals):
            rows.append(base(y,*YTA[y],'YTA',34,'Taulukko 4.5 (month 6 surgery/drug/RT columns = Taulukko 4.6, PDF p.35)','total',f'Cumulative % of lung cancer patients whose FIRST event by month {m} after diagnosis is: {en}',v,'%',month=m,event_fi=fi,n='not printed (region totals: Taulukko 3.3)'))
OUT['lung_report2024_first_event_cumulative_by_yta.csv']=rows
print('4.5 row sums (expect ~100):',min(sums),max(sums))
T46={'Leikkaushoito':[11.8,11.5,10.2,9.5,14.8],'Lääkehoito':[11.7,20.8,12.2,17.4,22.4],'Muu kuin palliatiivinen sädehoito':[21.9,16.4,15.6,13.3,14.9]}
ys=list(T45); idx={'Leikkaushoito':1,'Muu kuin palliatiivinen sädehoito':2,'Lääkehoito':3}
ok=all(abs(float(T45[y].split(';')[6].split()[idx[k]])-v)<1e-9 for k,vs in T46.items() for y,v in zip(ys,vs))
print('Taulukko 4.6 == 4.5 month-6 values:',ok)
# ---- Taulukko 5.1 (PDF p.36): age-standardised 1-year relative survival, 95% CI, by sex & YTA (follow-up years 2020-2022)
T51="""Etelä-Suomi|50.1 47.5 52.9|37.0 34.8 39.4|42.8 41.1 44.6
Itä-Suomi|50.1 45.6 55.1|38.9 35.7 42.4|42.7 40.0 45.5
Sisä-Suomi|50.5 46.3 55.0|44.3 40.9 48.0|46.8 44.1 49.6
Länsi-Suomi|47.4 43.3 51.7|38.5 35.5 41.9|41.9 39.4 44.5
Pohjois-Suomi|44.6 40.2 49.4|37.6 34.3 41.3|40.1 37.5 43.0
Koko maa|48.8 47.1 50.5|38.9 37.5 40.2|42.9 41.8 43.9"""
rows=[]
for line in T51.splitlines():
    y,*vals=line.split('|')
    for s,v in zip(['female','male','total'],vals):
        a,lo,hi=map(float,v.split())
        rows.append(base(y,*YTA[y],'YTA' if y!='Koko maa' else 'MAA',36,'Taulukko 5.1',s,'Lung cancer age-standardised 1-year relative survival, %',a,'%',lo=lo,hi=hi,cim='95% CI as printed in report',year='follow-up 2020-2022 (period analysis)'))
OUT['lung_report2024_survival_1y_by_yta.csv']=rows
# ---- Taulukko 5.3 (PDF p.39): 1-yr survival from start of first treatment by YTA, sex, treatment; n, 95% CI, RR vs South, p
T53={('male','Leikkaushoito'):"Etelä-Suomi 292 90.1 86.2 93 1 0.233;Itä-Suomi 147 90.6 84.3 94.5 0.91;Länsi-Suomi 118 90.2 83.5 94.3 1.02;Pohjois-Suomi 114 82.3 73.9 88.2 1.81;Sisä-Suomi 172 90.6 85.1 94.1 0.92",
 ('male','Muu kuin palliatiivinen sädehoito'):"Etelä-Suomi 604 37.3 33.5 41.2 1 <0.001;Itä-Suomi 197 35.1 28.3 41.9 1.11;Länsi-Suomi 215 52.6 45.7 59 0.68;Pohjois-Suomi 138 36.7 28.8 44.7 1.07;Sisä-Suomi 176 42.7 35.4 49.9 0.88",
 ('male','Lääkehoito'):"Etelä-Suomi 329 46.1 40.6 51.4 1 0.089;Itä-Suomi 250 40.6 34.4 46.6 1.17;Länsi-Suomi 200 47.3 40.3 54.1 0.96;Pohjois-Suomi 197 50.2 42.9 57 0.92;Sisä-Suomi 268 51.3 45.1 57.1 0.84",
 ('male','Palliatiivinen hoito'):"Etelä-Suomi 310 11.4 8.1 15.2 1 <0.001;Itä-Suomi 316 24.4 19.8 29.2 0.57;Sisä-Suomi 210 16.6 12 21.9 0.75",
 ('female','Leikkaushoito'):"Etelä-Suomi 294 94.1 90.7 96.3 1 0.405;Itä-Suomi 96 94.2 87.4 97.4 1.06;Länsi-Suomi 111 97.4 92.3 99.2 0.44;Pohjois-Suomi 82 95.1 87.6 98.1 0.83;Sisä-Suomi 139 97.3 92.9 99 0.46",
 ('female','Muu kuin palliatiivinen sädehoito'):"Etelä-Suomi 466 46.7 42.2 51.2 1 0.332;Itä-Suomi 79 56.4 44.3 66.8 0.7;Länsi-Suomi 129 50.8 41.9 59 0.89;Pohjois-Suomi 78 45.7 33.2 57.3 0.91;Sisä-Suomi 102 45.0 35.9 53.8 1",
 ('female','Lääkehoito'):"Etelä-Suomi 259 57.3 50.9 63.2 1 0.406;Itä-Suomi 138 52.2 43.5 60.2 1.11;Länsi-Suomi 80 47.9 36.8 58.2 1.33;Pohjois-Suomi 118 57.6 47.9 66.1 0.95;Sisä-Suomi 151 58.5 50.2 66 0.92",
 ('female','Palliatiivinen hoito'):"Etelä-Suomi 211 10.0 6.4 14.6 1 <0.001;Itä-Suomi 122 26.3 18.8 34.3 0.52;Sisä-Suomi 131 16.8 10.9 23.6 0.69"}
rows=[]
for (s,t),txt in T53.items():
    p=''
    for it in txt.split(';'):
        f=it.split(); y=f[0]; n,v,lo,hi,rr=f[1:6]
        if len(f)>6: p=f[6]
        rows.append(base(y,*YTA[y],'YTA',39,'Taulukko 5.3',s,f'Age-standardised 1-year survival from start of first treatment ({t}), %',float(v),'%',lo=float(lo),hi=float(hi),cim='95% CI as printed in report',n=int(n),
            treatment_fi=t,rr_mortality_vs_south=rr,p_value_group=p,year='diagnosed 1/2018-6/2022; follow-up max 1 yr',caveat='Palliative rows for Länsi/Pohjois not printed in the report' if 'Pall' in t else ''))
OUT['lung_report2024_survival_1y_by_treatment_yta.csv']=rows
# ---- write
for fn,rows in OUT.items():
    keys=[];[keys.append(k) for r in rows for k in r if k not in keys]
    with open(f'{D}/csv/{fn}','w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=keys); w.writeheader(); w.writerows(rows)
    print(fn,len(rows))
# ---- OCR cross-check: every transcribed number must appear in the independent OCR text of its page
def norm(s): return s.replace('Z','7').replace('I','1').replace('O','0').replace('o','0').replace('l','1').replace(',','.').replace(' ','')
ocr={}
def ocrtok(pg):
    if pg not in ocr:
        f=f'{D}/raw/lung2024_pages/p-{pg:02d}.ocr.txt'
        txt=norm(open(f).read()) if os.path.exists(f) else ''
        ocr[pg]=set(re.findall(r'\d+(?:\.\d+)?',txt.replace('|',' ').replace('-',' ').replace('–',' '))) if txt else set()
        # also split joined tokens
        raw=open(f).read() if os.path.exists(f) else ''
        for tok in re.split(r'[\s|()\-–]+',raw):
            ocr[pg].add(norm(tok))
    return ocr[pg]
tot=miss=0; misses=[]
for fn,rows in OUT.items():
    for r in rows:
        pg=r['page']
        for k in ('value','ci95_low','ci95_high','n','q1','q3'):
            v=r.get(k,'')
            if v in ('',None) or isinstance(v,str): continue
            if k.startswith('ci95') and 'computed' in r.get('ci_method',''): continue  # our own Wilson CIs are not in the PDF
            cands={str(v),f'{v:.1f}' if isinstance(v,float) else str(v), str(int(v)) if float(v).is_integer() else str(v)}
            if isinstance(v,int) and v>=1000: cands.add(f'{v//1000}{v%1000:03d}')
            tot+=1
            if not (cands & ocrtok(pg)): miss+=1; misses.append((fn.split('_',2)[2][:30],pg,r['region_name_fi'],r['sex'],r.get('treatment_fi',r.get('event_fi','')),k,v))
print(f'OCR cross-check: {tot-miss}/{tot} transcribed numbers found verbatim in independent OCR text; {miss} not found (OCR dropped/misread; each confirmed visually against the render, list in raw/lung2024_pages/ocr_crosscheck_misses.tsv)')
with open(f'{D}/raw/lung2024_pages/ocr_crosscheck_misses.tsv','w') as fh:
    for m in misses: fh.write('\t'.join(map(str,m))+'\n')
