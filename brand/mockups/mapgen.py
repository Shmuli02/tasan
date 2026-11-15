"""Generate inline SVG choropleth of Finland wellbeing counties for mockups.
Geometry: read-only from app/src/content/counties.json (Statistics Finland).
Values: crude curative share, Keuhkosyöpä Suomessa 2019-2023 Taulukko 11 (data/csv/lung_report2026_treatment_by_wsc.csv)."""
import json, csv, math
ROOT='/workspace/junction-new'
geo=json.load(open(f'{ROOT}/app/src/content/counties.json'))
vals={}
for r in csv.DictReader(open(f'{ROOT}/data/csv/lung_report2026_treatment_by_wsc.csv')):
    if r['treatment_group_fi']=='Parantava' and r['sex']=='total':
        vals[r['region_code']]=(float(r['value']),r['region'])
RAMP=['var(--tz-map-1)','var(--tz-map-2)','var(--tz-map-3)','var(--tz-map-4)','var(--tz-map-5)','var(--tz-map-6)']
def step(v):  # lowest share -> darkest
    for i,b in enumerate([20,23,26,29,32]):
        if v<b: return 5-i
    return 0
def polys(f):
    g=f['geometry']; return [g['coordinates']] if g['type']=='Polygon' else g['coordinates']
def dp(pts,eps):
    if len(pts)<3: return pts
    (x1,y1),(x2,y2)=pts[0],pts[-1]; dx,dy=x2-x1,y2-y1; L=math.hypot(dx,dy) or 1e-9
    i,dm=0,0
    for k in range(1,len(pts)-1):
        d=abs(dy*pts[k][0]-dx*pts[k][1]+x2*y1-y2*x1)/L
        if d>dm: i,dm=k,d
    if dm>eps: return dp(pts[:i+1],eps)[:-1]+dp(pts[i:],eps)
    return [pts[0],pts[-1]]
def svg(W,H,ids=None,selected=None,pad=8,eps=0.6,cls='map'):
    feats=[f for f in geo['features'] if ids is None or f['properties']['id'] in ids]
    k=math.cos(math.radians(64 if ids is None else 60.3))
    xs=[p[0]*k for f in feats for P in polys(f) for R in P for p in R]; ys=[p[1] for f in feats for P in polys(f) for R in P for p in R]
    s=min((W-2*pad)/(max(xs)-min(xs)),(H-2*pad)/(max(ys)-min(ys)))
    ox=(W-(max(xs)-min(xs))*s)/2; oy=(H-(max(ys)-min(ys))*s)/2
    out=[f'<svg class="{cls}" viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">',
         '<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#D9D4C9"/><line x1="0" y1="0" x2="0" y2="6" stroke="#B9B2A4" stroke-width="1.5"/></pattern></defs>']
    sel=''
    for f in feats:
        fid=f['properties']['id']; d=''
        for P in polys(f):
            for R in P:
                pts=[((p[0]*k-min(xs))*s+ox,(max(ys)-p[1])*s+oy) for p in R]
                h=len(pts)//2
                pts=dp(pts[:h+1],eps)[:-1]+dp(pts[h:],eps)
                if len(pts)<3: continue
                area=abs(sum(pts[i][0]*pts[i-1][1]-pts[i-1][0]*pts[i][1] for i in range(len(pts))))/2
                if area<1.5: continue
                d+='M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)+'Z'
        fill=RAMP[step(vals[fid][0])] if fid in vals else 'url(#hatch)'
        p=f'<path d="{d}" fill="{fill}" stroke="#fff" stroke-width="0.9" stroke-linejoin="round"><title>{f["properties"]["name_en"]}</title></path>'
        if fid==selected: sel=f'<path d="{d}" fill="none" stroke="var(--tz-map-selected)" stroke-width="2.5" stroke-linejoin="round"/>'
        out.append(p)
    out.append(sel); out.append('</svg>')
    return ''.join(out)
if __name__=='__main__':
    print(len(svg(480,620)))
