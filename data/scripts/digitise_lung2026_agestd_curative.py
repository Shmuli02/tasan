"""CHART-DIGITISED ESTIMATES (not published numbers): age-standardised share of lung cancer patients with CURATIVE treatment
(Parantava) within 12 months, with 95% CI, by sex x wellbeing services county (Kuva 16) and by sex x collaborative area (Kuva 15),
from 'Keuhkosyöpä Suomessa 2019-2023' (Syöpärekisteri/FICAN, publ. 23.4.2026)
https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html  (figures saved raw/lung_figs/img2026_176.png = Kuva 15, img2026_177.png = Kuva 16).
Method: x-axis calibrated from the axis tick marks (pixel positions of 0/20/40/60 resp. 0..50); point = centre of the filled dot; CI = extent of the
coloured horizontal bar at the dot's row. Resolution about 0.35 pp per pixel; treat values as +/-1 pp. The report does NOT publish these numbers in tables."""
from PIL import Image; import csv, os, json
D=os.path.join(os.path.dirname(__file__),'..')
URL='https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html'
REG={r['title']['fi']:(r['code'],r['title']['en']) for r in json.load(open(f'{D}/raw/sotkanet_regions.json')) if r['category']=='HYVINVOINTIALUE'}
isb=lambda p: p[2]>120 and p[0]<60 and 80<p[1]<160 and p[2]-p[0]>80
def ticks(im,y):
    w=im.size[0]; xs=[x for x in range(w) if sum(im.getpixel((x,y)))<300]; g=[];s=p=None
    for x in xs:
        if s is None: s=p=x
        elif x==p+1: p=x
        else: g.append((s+p)/2); s=p=x
    g.append((s+p)/2); return g
def points(im,x0,x1,y0,y1):
    ys=[y for y in range(y0,y1) if any(isb(im.getpixel((x,y))) for x in range(x0,x1))]
    cl=[];s=p=None
    for y in ys:
        if s is None: s=p=y
        elif y<=p+2: p=y
        else: cl.append((s,p)); s=p=y
    if s is not None: cl.append((s,p))
    out=[]
    for a,b in cl:
        if b-a<6: continue
        col={x:sum(1 for y in range(a,b+1) if isb(im.getpixel((x,y)))) for x in range(x0,x1)}
        mx=max(col.values()); dot=[x for x,v in col.items() if v>=0.8*mx]; xc=sum(dot)/len(dot)
        yc=(a+b)//2
        bar=[x for x in range(x0,x1) if isb(im.getpixel((x,yc)))]
        out.append((yc,xc,min(bar),max(bar)))
    return out
rows=[]
def emit(name_fi,sex,pt,cal,fig,rtype):
    yc,xc,lo,hi=pt; f=lambda px: round((px-cal[0])/cal[1],1)
    if rtype=='HYVINVOINTIALUE':
        k=name_fi if name_fi=='Helsingin kaupunki' else name_fi+' hyvinvointialue'; code,en=REG[k]
    else: k=name_fi; code,en={'Etelä-Suomen yhteistyöalue':('YTA-ETELA','South Finland collaborative area (YTA)'),'Itä-Suomen yhteistyöalue':('YTA-ITA','East Finland collaborative area (YTA)'),'Länsi-Suomen yhteistyöalue':('YTA-LANSI','West Finland collaborative area (YTA)'),'Pohjois-Suomen yhteistyöalue':('YTA-POHJOIS','North Finland collaborative area (YTA)'),'Sisä-Suomen yhteistyöalue':('YTA-SISA','Inland Finland collaborative area (YTA)')}[k]
    rows.append(dict(region=en,region_name_fi=k,region_code=code,region_type=rtype,year='2019-2023 (diagnosis years; 12-month follow-up)',sex=sex,
        indicator='Lung cancer patients with curative treatment (surgery or curative radiotherapy) within 12 months, AGE-STANDARDISED % - CHART-DIGITISED ESTIMATE',
        value=f(xc),ci95_low=f(lo),ci95_high=f(hi),unit='% (approx., +/-1 pp)',ci_method='95% CI as drawn in report figure (digitised by us)',
        method='pixel digitisation of figure; report publishes no table for these values',source_url=URL,source_table=f'Keuhkosyöpä Suomessa 2019-2023 (publ. 23.4.2026), {fig} (Parantava panel)'))
# Kuva 16: by wellbeing county
im=Image.open(f'{D}/raw/lung_figs/img2026_177.png').convert('RGB')
t=ticks(im,778); assert len(t)==24
blocks=[(60,771,['Vantaan ja Keravan','Päijät-Hämeen','Länsi-Uudenmaan','Kymenlaakson','Keski-Uudenmaan','Itä-Uudenmaan','Helsingin kaupunki','Etelä-Karjalan']),
        (790,1174,['Pohjois-Savon','Pohjois-Karjalan','Keski-Suomen','Etelä-Savon']),
        (1190,1494,['Varsinais-Suomen','Satakunnan','Pohjanmaan']),
        (1512,1897,['Pohjois-Pohjanmaan','Lapin','Keski-Pohjanmaan','Kainuun']),
        (1915,2216,['Pirkanmaan','Kanta-Hämeen','Etelä-Pohjanmaan'])]
for sex,pi in (('male',0),('female',3)):
    tk=t[pi*4:pi*4+4]; cal=(tk[0],(tk[3]-tk[0])/60)
    for y0,y1,names in blocks:
        pts=points(im,int(tk[0])-8,int(tk[3])+15,y0+20,y1)
        # map points to row names by vertical position (rows equally spaced within block)
        nm=[x for x in names if x!='Kainuun']  # Kainuu: no curative point drawn (suppressed, small n)
        assert len(pts)==len(nm),(sex,names[0],len(pts))
        for x,p in zip(nm,pts): emit(x,sex,p,cal,'Kuva 16','HYVINVOINTIALUE')
# Kuva 15: by collaborative area
im=Image.open(f'{D}/raw/lung_figs/img2026_176.png').convert('RGB')
names=['Etelä-Suomen yhteistyöalue','Itä-Suomen yhteistyöalue','Länsi-Suomen yhteistyöalue','Pohjois-Suomen yhteistyöalue','Sisä-Suomen yhteistyöalue']
for sex,yaxis,ytop in (('male',705,110),('female',1448,850)):
    tk=ticks(im,yaxis+6)[:6]; cal=(tk[0],(tk[5]-tk[0])/50)
    pts=points(im,int(tk[0])-8,int(tk[5])+10,ytop,yaxis)
    assert len(pts)==5,(sex,len(pts))
    for nm,p in zip(names,pts): emit(nm,sex,p,cal,'Kuva 15','YTA')
with open(f'{D}/csv/lung_report2026_curative_agestd_by_sex_chart_estimate.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r['sex'][0],r['region_name_fi'][:22].ljust(22),r['value'],r['ci95_low'],r['ci95_high'])
