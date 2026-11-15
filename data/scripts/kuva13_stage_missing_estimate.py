"""CHART-DERIVED ESTIMATE (not a published number): share of lung cancers with NO stage information ('Ei tietoa', blue segment)
by wellbeing services county, measured from pixel lengths in Kuva 13 of the 2026 lung report
(https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html, image saved raw/lung_figs/Kuva_13.png).
Bar origin x=553 (0 %), bar end x=1319 (100 %); precision about +/-0.5 pp. Order = order of bars in the figure (top to bottom)."""
from PIL import Image; import csv, os, json
D=os.path.join(os.path.dirname(__file__),'..')
NAMES=['Etelä-Karjalan hyvinvointialue','Helsingin kaupunki','Itä-Uudenmaan hyvinvointialue','Keski-Uudenmaan hyvinvointialue','Kymenlaakson hyvinvointialue','Länsi-Uudenmaan hyvinvointialue','Päijät-Hämeen hyvinvointialue','Vantaan ja Keravan hyvinvointialue',
 'Etelä-Savon hyvinvointialue','Keski-Suomen hyvinvointialue','Pohjois-Karjalan hyvinvointialue','Pohjois-Savon hyvinvointialue','Pohjanmaan hyvinvointialue','Satakunnan hyvinvointialue','Varsinais-Suomen hyvinvointialue',
 'Kainuun hyvinvointialue','Keski-Pohjanmaan hyvinvointialue','Lapin hyvinvointialue','Pohjois-Pohjanmaan hyvinvointialue','Etelä-Pohjanmaan hyvinvointialue','Kanta-Hämeen hyvinvointialue','Pirkanmaan hyvinvointialue']
REG={r['title']['fi']:(r['code'],r['title']['en']) for r in json.load(open(f'{D}/raw/sotkanet_regions.json')) if r['category']=='HYVINVOINTIALUE'}
im=Image.open(f'{D}/raw/lung_figs/Kuva_13.png').convert('RGB'); w,h=im.size
isb=lambda p: p[2]>130 and p[0]<40 and 90<p[1]<150
ys=[y for y in range(h) if isb(im.getpixel((600,y)))]
bars=[];s=p=ys[0]
for y in ys[1:]:
    if y!=p+1: bars.append((s,p)); s=y
    p=y
bars.append((s,p)); assert len(bars)==22
X0,X1=553,1319; rows=[]
for nm,(a,b) in zip(NAMES,bars):
    y=(a+b)//2; xb=max(x for x in range(X0,w) if isb(im.getpixel((x,y))))
    v=round(100*(xb-X0+1)/(X1-X0+1),0)
    c,e=REG[nm]
    rows.append(dict(region=e,region_name_fi=nm,region_code=c,region_type='HYVINVOINTIALUE',year='2019-2023 (diagnosis years)',sex='total',
      indicator='Lung cancers with no stage information at diagnosis (Ei tietoa), % - CHART-DERIVED ESTIMATE',value=int(v),unit='% (approx., +/-1 pp)',
      method='pixel measurement of Kuva 13 bar segments by us; the report publishes no per-county number',denominator='not published per county',
      source_url='https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html',source_table='Keuhkosyöpä Suomessa 2019-2023 (publ. 23.4.2026), Kuva 13 (chart only)'))
with open(f'{D}/csv/lung_report2026_stage_missing_by_wsc_chart_estimate.csv','w',newline='') as fh:
    wr=csv.DictWriter(fh,fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
for r in sorted(rows,key=lambda r:r['value']): print(r['value'],r['region_name_fi'])
