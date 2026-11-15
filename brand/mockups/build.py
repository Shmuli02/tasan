import sys, csv
sys.path.insert(0,'.')
from mapgen import svg, vals, step
from icons import icon
ROOT='/workspace/junction-new'
LOGO=open(f'{ROOT}/brand/logo.svg').read().replace('<svg ','<svg class="logo" ')
SHORT={'01':'East Uusimaa','02':'Central Uusimaa','03':'West Uusimaa','04':'Vantaa-Kerava','05':'Southwest Finland','06':'Satakunta','07':'Kanta-Häme','08':'Pirkanmaa','09':'Päijät-Häme','10':'Kymenlaakso','11':'South Karelia','12':'South Savo','13':'North Savo','14':'North Karelia','15':'Central Finland','16':'South Ostrobothnia','17':'Ostrobothnia','18':'Central Ostrob.','19':'North Ostrobothnia','20':'Kainuu','21':'Lapland','90':'Helsinki'}
FACT_LABEL={'21':'lung_curative_lapland','04':'lung_curative_vantaa_kerava','11':'lung_curative_south_karelia','10':'lung_curative_kymenlaakso','90':'lung_curative_helsinki'}
RAMPHEX=['#E6F2EF','#BCDCD6','#86BFB9','#4F9C9C','#2D6B7D','#16233F']
TABS=[('Overview','map'),('Counties','building'),('Pathway','route'),('Tasan Live','activity'),('Simulate','sliders'),('Pilot','clip')]
def topbar(active):
    t=''.join(f'<div class="tab{" on" if n==active else ""}">{icon(i)}{n}{"<span class=ex>EXAMPLE</span>" if n=="Tasan Live" else ""}</div>' for n,i in TABS)
    return f'''<header class="topbar">{LOGO}<nav class="tabs">{t}</nav><div class="right"><div class="lang"><span>FI</span><span class="on">EN</span></div><span class="badge b-verda">AI on Verda · EU-hosted</span></div></header>'''
def page(title,css,body):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title><link rel="stylesheet" href="app.css"><link rel="stylesheet" href="{css}"></head><body>{body}</body></html>'

def panel(ctx, msgs, sugg, dark=False):
    return f'''<aside class="panel{' dark' if dark else ''}"><div class="panel-head"><div class="panel-title"><span class="spark">{icon('sparkles')}</span>Ask Tasan<span class="badge b-ex" style="margin-left:auto">EXAMPLE chat</span></div>
<div class="ctx">Context <b>{ctx}</b></div></div><div class="msgs">{msgs}</div>
<div class="sugg">{''.join(f'<span>{s}</span>' for s in sugg)}</div>
<div class="input">Ask about any county…<span class="send">{icon('send')}</span></div>
<div class="panel-foot"><span>Cites data/facts.json only · refuses without data</span><span>AI on Verda · EU-hosted</span></div></aside>'''
def C(fid): return f'<span class="cite">{fid}</span>'

def overview():
    rows=sorted(vals.items(), key=lambda kv: kv[1][0])
    scale=lambda v: v/40*100
    br=''
    for code,(v,_) in rows:
        lab=f'{v:.1f}%' if code in FACT_LABEL else ''
        br+=f'<div class="brow{" sel" if code=="21" else ""}"><span class="nm">{SHORT[code]}</span><div class="track"><div class="bar" style="width:{scale(v):.2f}%;background:{RAMPHEX[step(v)]}"></div></div><span class="v">{lab}</span></div>'
    grid=''.join(f'<div class="g" style="left:{scale(x)}%"><span>{x}%</span></div>' for x in (0,10,20,30,40))
    axis=f'<div class="axis">{grid}<div class="nat" style="left:{scale(27.0)}%"><span>National 27.0%</span></div></div>'
    def ci(lo,hi,v,col,lab):
        s=lambda x:(x-10)/40*100
        return f'<div class="ci-track"><div class="w" style="left:{s(lo)}%;width:{s(hi)-s(lo)}%"></div><div class="d" style="left:{s(v)}%;background:{col}"></div><div class="l" style="left:{s(v)}%">{lab}</div></div>'
    mapsvg=svg(330,560,selected='21')
    inset=svg(140,92,ids={'01','02','03','04','90'},pad=4,eps=0.3,cls='inset-map')
    msgs=f'''<div class="bubble me">Why is Lapland behind?</div>
<div class="bubble ai">Lapland: <b>18.5%</b> had a curative-treatment record vs <b>27.0%</b> nationally (2019–2023) {C('lung_curative_lapland')} {C('lung_curative_national')}<br><br>Age-adjusted, men: about <b>16</b> vs about <b>30</b> per 100 in Vantaa-Kerava; intervals don't overlap {C('lung_curative_agestd_lapland_men')}<br><br>Not stage-adjusted: no public data {C('nodata_stage_adjusted_comparison')}
<div class="meta">{icon('shield')} 4 facts cited · Keuhkosyöpä Suomessa 2019–2023</div></div>
<div class="bubble me">How many lives would this save?</div>
<div class="bubble refuse"><div class="rl">{icon('eye-off')} No sourced answer</div>No public source estimates lives saved, so Tasan doesn't either {C('nodata_lives_saved')}</div>'''
    body=topbar('Overview')+f'''<div class="shell"><main class="main">
<div class="hdr"><div><div class="kicker">Lung cancer · Finland · diagnosed 2019–2023</div><h1>Curative care is not even across Finland</h1></div>
<div class="chips" style="gap:10px"><div class="seg"><span class="on">Crude share</span><span>Age-adjusted</span></div><span class="btn-ghost">{icon('info')}Sources</span></div></div>
<section class="kpis">
 <div class="card kpi hero"><div class="val num">~65<small>/yr</small></div><div style="display:flex;flex-direction:column;gap:8px"><div class="lbl">more lung cancer patients a year would have had a curative-treatment record if every county below the national share (27.0%) had reached it</div><div class="foot"><span class="badge b-comp">Computed by Tasan · crude</span><span class="src">people_number_national</span></div></div></div>
 <div class="card kpi"><div class="top"><div class="lbl">Lapland · curative-treatment record</div><span class="ico">{icon('map')}</span></div><div class="val num">18.5<small>%</small></div><div class="cmp">National <b class="num">27.0%</b></div><div class="foot"><span class="src">lung_curative_lapland</span><span class="src">lung_curative_national</span></div></div>
 <div class="card kpi"><div class="top"><div class="lbl">More patients a year in Lapland, at the national share</div><span class="ico">{icon('users')}</span></div><div class="val num">~12<small>/yr</small></div><div class="cmp">Computed by Tasan · crude</div><div class="foot"><span class="src">people_number_lapland</span></div></div>
 <div class="card kpi"><div class="top"><div class="lbl">Public reports of patients treated within 6 weeks</div><span class="ico">{icon('eye-off')}</span></div><div class="val num">0</div><div class="cmp">Any region, any cancer</div><div class="foot"><span class="badge b-nodata">Data gap</span><span class="src">nodata_regional_target_compliance</span></div></div>
</section>
<section class="grid3">
 <div class="card mapcard"><div class="card-head"><div><h2>Curative-treatment share by county</h2><div class="sub">Darker = lower share · click a county</div></div><span class="src">Taulukko 11</span></div>
  <div class="mapwrap">{mapsvg}<div class="pin" style="left:296px;top:66px">Lapland<b>18.5%</b></div><div class="inset"><div class="t">Helsinki region</div>{inset}</div></div>
  <div class="legend"><span>lower</span><span class="ramp">{''.join(f'<i style="background:{c}"></i>' for c in reversed(RAMPHEX))}</span><span>higher</span><span style="margin-left:auto"><span class="nd"></span>No public data</span></div></div>
 <div class="card" style="display:flex;flex-direction:column"><div class="card-head"><div><h2>All counties, ranked</h2><div class="sub">Share with a curative-treatment record within 12 months (crude)</div></div><span class="src">Taulukko 11</span></div>
  <div class="bars" style="margin-top:10px">{axis}{br}</div></div>
 <div style="display:flex;flex-direction:column;gap:20px;min-height:0">
  <div class="card"><div class="card-head"><div><h2>Age-adjusted, same gap</h2><div class="sub">Curative share per 100 patients</div></div><span class="badge b-est">Chart estimate</span></div>
   <div class="sexlbl">Men</div>
   <div class="ci-row"><span class="nm">Lapland</span>{ci(12.7,20.4,16.2,'#16233F','~16.2')}</div>
   <div class="ci-row"><span class="nm">Vantaa-Kerava</span>{ci(24.2,36.1,29.8,'#3A9A9A','~29.8')}</div>
   <div class="sexlbl">Women</div>
   <div class="ci-row"><span class="nm">Lapland</span>{ci(17.9,29.0,23.1,'#16233F','~23.1')}</div>
   <div class="ci-row"><span class="nm">Vantaa-Kerava</span>{ci(33.1,47.0,39.7,'#3A9A9A','~39.7')}</div>
   <div class="ci-axis"><span></span><div><span>10%</span><span>20%</span><span>30%</span><span>40%</span><span>50%</span></div></div>
   <div class="note">Read from report chart (±1 pp) · 95% intervals don't overlap</div>
   <div class="chips" style="margin-top:8px"><span class="src">lung_curative_agestd_lapland_men</span><span class="src">…_vk_men</span><span class="src">…_women</span></div></div>
  <div class="card" style="flex:1"><div class="card-head"><div><h2>Where the data goes dark</h2><div class="sub">Referral → treatment, lung cancer</div></div></div>
   <div class="pw"><div class="st dark">{icon('clip')}Referral</div><div class="st dark">{icon('scan')}Imaging</div><div class="st dark">{icon('micro')}Biopsy</div><div class="st dark">{icon('users')}MDT</div><div class="st lit">{icon('activity')}Treated</div></div>
   <div class="target">THL target: 6 weeks referral → treatment</div>
   <div class="darklbl"><span class="badge b-nodata">No public data</span>by county, any step</div>
   <div class="chips" style="margin-top:10px"><span class="src">nodata_referral_to_diagnosis</span><span class="src">thl_6wk_referral_to_treatment</span></div></div>
 </div>
</section></main>
{panel('Finland · Overview', msgs, ['Draft Lapland pilot brief','Where does data go dark?','Compare Kymenlaakso'])}</div>'''
    open('overview.html','w').write(page('Tasan mockup – Overview','overview.css',body))

if __name__=='__main__':
    overview()
    if 'live' in sys.argv or True:
        try:
            import live; live.build()
        except ImportError: pass
        try:
            import howwebuilt; howwebuilt.build()
        except ImportError: pass
