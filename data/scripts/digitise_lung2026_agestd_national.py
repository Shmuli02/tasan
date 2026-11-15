"""CHART-DIGITISED national reference lines (dashed 'koko maan osuus') in the Parantava panels of Kuva 15 (by YTA) and Kuva 16 (by county),
Keuhkosyöpä Suomessa 2019-2023 (publ. 23.4.2026) https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html
Method: same axis calibration as digitise_lung2026_agestd_curative.py; the dashed line = the panel column with the most dark pixels (2-px wide line; centre used).
Finding: Kuva 15 lines differ by sex (men ~24.9, women ~30.0 = sex-specific national age-standardised share).
Kuva 16 lines sit at ~26.9 in BOTH sex panels, i.e. they match the crude all-patient national 27.0% (Taulukko 10), so Kuva 16's line is not sex-specific (our reading)."""
from PIL import Image; import csv, os
D=os.path.join(os.path.dirname(__file__),'..')
def ticks(im,y):
    w=im.size[0]; xs=[x for x in range(w) if sum(im.getpixel((x,y)))<300]; g=[];s=p=None
    for x in xs:
        if s is None: s=p=x
        elif x==p+1: p=x
        else: g.append((s+p)/2); s=p=x
    g.append((s+p)/2); return g
def dash(im,x0,x1,y0,y1):
    sc=[(sum(1 for y in range(y0,y1) if sum(im.getpixel((x,y)))<200),x) for x in range(int(x0)+3,int(x1))]
    m=max(sc)[0]; xs=[x for n,x in sc if n>=0.9*m]; return sum(xs)/len(xs)
rows=[]; URL='https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html'
im=Image.open(f'{D}/raw/lung_figs/img2026_176.png').convert('RGB')
for sex,ya,yt in (('male',705,110),('female',1448,850)):
    tk=ticks(im,ya+6)[:6]; v=round((dash(im,tk[0],tk[5],yt,ya-5)-tk[0])/((tk[5]-tk[0])/50),1)
    rows.append(dict(region='Finland',region_code='358',sex=sex,value=v,figure='Kuva 15',interpretation='sex-specific national age-standardised curative share (reference line)'))
im=Image.open(f'{D}/raw/lung_figs/img2026_177.png').convert('RGB'); t=ticks(im,778)
for sex,pi in (('male',0),('female',3)):
    tk=t[pi*4:pi*4+4]; v=round((dash(im,tk[0],tk[3],60,771)-tk[0])/((tk[3]-tk[0])/60),1)
    rows.append(dict(region='Finland',region_code='358',sex=sex,value=v,figure='Kuva 16',interpretation='reference line drawn identically in both sex panels; matches crude all-patient national 27.0% (Taulukko 10) - not sex-specific (Tasan reading)'))
for r in rows:
    r.update(year='2019-2023 (diagnosis years; 12-month follow-up)',indicator='National reference line, lung curative-treatment share, % - CHART-DIGITISED ESTIMATE',unit='% (approx., +/-1 pp)',
             measure_type='chart_estimate',source_url=URL,source_table=f"Keuhkosyöpä Suomessa 2019-2023, {r['figure']} (Parantava panel, dashed line)")
with open(f'{D}/csv/lung_report2026_curative_agestd_national_chart_estimate.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r['figure'],r['sex'],r['value'])
