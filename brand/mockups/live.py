import math
from icons import icon
import build as B
COL={'ok':'#4CC2A4','risk':'#E6C25A','al':'#F2A65A','cr':'#FF6B5A'}
def ring(day,size=28,stroke=4,label=False,of=42):
    r=(size-stroke)/2; c=2*math.pi*r; f=min(day/of,1)
    col=COL['ok'] if day<21 else COL['risk'] if day<28 else COL['al'] if day<42 else COL['cr']
    ticks=''
    if label:
        for d in (21,28):
            a=2*math.pi*d/of-math.pi/2; x1=size/2+(r-stroke)*math.cos(a); y1=size/2+(r-stroke)*math.sin(a); x2=size/2+(r+stroke)*math.cos(a); y2=size/2+(r+stroke)*math.sin(a)
            ticks+=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#6F7D97" stroke-width="2"/>'
    txt=(f'<text x="50%" y="47%" text-anchor="middle" font-family="JetBrains Mono" font-weight="600" font-size="28" fill="#fff">D{day}</text>'
         f'<text x="50%" y="64%" text-anchor="middle" font-family="JetBrains Mono" font-size="11" fill="#A9B4C8">of 42 · 6 wk</text>') if label else ''
    glow=f' style="filter:drop-shadow(0 0 6px {col}88)"' if label else ''
    return (f'<svg class="ring" width="{size}" height="{size}" viewBox="0 0 {size} {size}"><circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="#2A3B60" stroke-width="{stroke}"/>'
            f'<circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="{col}" stroke-width="{stroke}" stroke-linecap="round" stroke-dasharray="{c*f:.1f} {c:.1f}" transform="rotate(-90 {size/2} {size/2})"{glow}/>{ticks}{txt}</svg>')
def spark(pts,col,w=92,h=34):
    mx,mn=max(pts),min(pts); xs=[i*(w-4)/(len(pts)-1)+2 for i in range(len(pts))]; ys=[h-3-(p-mn)/(mx-mn or 1)*(h-8) for p in pts]
    d='M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in zip(xs,ys))
    return f'<svg class="spk" width="{w}" height="{h}"><path d="{d} L{xs[-1]:.1f},{h} L{xs[0]:.1f},{h}Z" fill="{col}" opacity=".12"/><path d="{d}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round"/><circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="3" fill="{col}"/></svg>'
STEPN=['Referral','Imaging','Biopsy','MDT','Treatment']
# EXAMPLE patients (simulated)
P=[('P-0207',28,1,'CT slot','scan','al','Alert','AK'),
   ('P-0193',34,2,'Biopsy result','micro','al','Alert','MV'),
   ('P-0188',39,3,'MDT slot','users','cr','At risk','AK'),
   ('P-0211',22,1,'PET-CT','scan','risk','Watch','—'),
   ('P-0199',17,2,'—','clock','ok','On track','MV'),
   ('P-0214',12,1,'—','clock','ok','On track','AK'),
   ('P-0201',25,3,'MDT slot','users','risk','Watch','MV'),
   ('P-0216',8,0,'—','clock','ok','On track','—'),
   ('P-0185',31,4,'—','clock','ok','Treated','AK'),
   ('P-0218',3,0,'—','clock','ok','On track','—'),
   ('P-0209',19,2,'—','clock','ok','On track','MV')]
def build():
    rows=''
    for i,(pid,d,s,blk,ic,st,stl,nav) in enumerate(P):
        steps=''.join(f'<i class="{"d" if k<s else "c" if k==s else ""}"></i>' for k in range(5))
        b=f'<span class="blk" style="color:{COL[st] if blk!="—" else ""}">{icon(ic)}{blk}</span>' if blk!='—' else '<span class="blk">—</span>'
        rows+=f'<tr class="{"sel" if i==0 else ""}"><td>{ring(d)}</td><td class="id">{pid}</td><td>D{d:02d}</td><td><span class="steps">{steps}</span><span class="stx">{STEPN[s]}</span></td><td>{b}</td><td><span class="nav"><i>{nav if nav!="—" else "+"}</i>{"Navigator" if nav!="—" else "Unassigned"}</span></td><td><span class="st {st}">{stl}</span></td></tr>'
    alerts=[('P-0207','#F2A65A','DAY 28','scan','CT slot not booked','rgba(242,166,90,.16)'),
            ('P-0193','#F2A65A','DAY 34','micro','Biopsy result pending 6 d','rgba(242,166,90,.16)'),
            ('P-0188','#FF6B5A','DAY 39','users','No MDT slot before day 42','rgba(255,107,90,.16)')]
    arows=''.join(f'<div class="arow"><div class="bar" style="background:{c}"></div><div><div class="t1">{pid} <span class="dchip" style="color:{c};background:{bg}">{dd}</span></div><div class="t2">{icon(ic)}{why}</div></div><span class="btn gh">{icon("user-plus")}Assign</span></div>' for pid,c,dd,ic,why,bg in alerts)
    blk=[('CT slot','scan',5,'#F2A65A'),('Biopsy','micro',3,'#E6C25A'),('MDT slot','users',4,'#FF6B5A'),('PET-CT','scan',2,'#5CC4C4'),('Patient-side','clock',1,'#6F7D97')]
    hbs=''.join(f'<div class="hb"><span>{icon(ic)}{n}</span><div class="bt"><i style="width:{v/5*100}%;background:{c}"></i></div><b>{v}</b></div>' for n,ic,v,c in blk)
    # trend svg
    wk=[48,51,50,55,58,57,61,64,63,67,66,69]; W,H=420,150
    xs=[30+i*(W-40)/11 for i in range(12)]; ys=[H-20-(v-40)/40*(H-30) for v in wk]
    grid=''.join(f'<line x1="30" x2="{W-10}" y1="{H-20-(g-40)/40*(H-30):.1f}" y2="{H-20-(g-40)/40*(H-30):.1f}" stroke="#2A3B60"/><text x="0" y="{H-16-(g-40)/40*(H-30):.1f}" font-family="JetBrains Mono" font-size="10" fill="#6F7D97">{g}%</text>' for g in (40,60,80))
    d='M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in zip(xs,ys))
    base=f'<line x1="30" x2="{W-10}" y1="{ys[0]:.1f}" y2="{ys[0]:.1f}" stroke="#A9B4C8" stroke-dasharray="4 4"/><text x="{W-12}" y="{ys[0]+14:.1f}" text-anchor="end" font-family="JetBrains Mono" font-size="10" fill="#A9B4C8">week-1 baseline</text>'
    xl=''.join(f'<text x="{xs[i]:.1f}" y="{H-2}" text-anchor="middle" font-family="JetBrains Mono" font-size="10" fill="#6F7D97">w{i+1}</text>' for i in (0,3,7,11))
    trend=f'<svg width="{W}" height="{H}">{grid}{base}<path d="{d} L{xs[-1]:.1f},{H-20} L{xs[0]:.1f},{H-20}Z" fill="url(#tg)"/><defs><linearGradient id="tg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#5CC4C4" stop-opacity=".35"/><stop offset="1" stop-color="#5CC4C4" stop-opacity="0"/></linearGradient></defs><path d="{d}" fill="none" stroke="#5CC4C4" stroke-width="2.5" stroke-linejoin="round"/><circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="4.5" fill="#5CC4C4" stroke="#16233F" stroke-width="2"/>{xl}</svg>'
    ev=[('09:42:07','#F2A65A','<b>P-0207</b> <b class="a">DAY-28 ALERT</b> CT not booked',' new al'),
        ('09:41:52','#4CC2A4','<b>P-0185</b> surgery done → clock stopped D31',''),
        ('09:39:10','#5CC4C4','<b>P-0214</b> CT booked for D14',''),
        ('09:36:44','#E6C25A','<b>P-0211</b> D22 · PET-CT wait &gt;5 d',''),
        ('09:31:02','#5CC4C4','<b>P-0218</b> referral received → clock D0',''),
        ('09:28:15','#4CC2A4','<b>P-0199</b> biopsy sample sent',''),
        ('09:20:48','#F2A65A','<b>P-0193</b> <b class="a">ALERT</b> biopsy result D34',''),
        ('09:14:33','#5CC4C4','<b>P-0201</b> MDT request · Thu slot',''),
        ('09:02:19','#FF6B5A','<b>P-0188</b> <b class="a" style="color:#FF6B5A">AT RISK</b> no MDT slot ≤ D42',''),
        ('08:55:01','#4CC2A4','<b>P-0209</b> navigator call done',''),
        ('08:47:36','#5CC4C4','<b>P-0216</b> imaging ordered',''),
        ('08:40:12','#4CC2A4','<b>P-0185</b> MDT decision: surgery',''),
        ('08:31:50','#5CC4C4','<b>P-0214</b> referral triaged → urgent',''),
        ('08:22:04','#4CC2A4','<b>P-0199</b> CT read · D15',''),
        ('08:15:27','#5CC4C4','<b>P-0218</b> navigator assigned','')]
    evs=''.join(f'<div class="ev{c}"><span class="tm">{t}</span><span class="dt" style="background:{col}"></span><span>{x}</span></div>' for t,col,x,c in ev)
    msgs=f'''<div class="bubble me">What's blocking P-0207?</div>
<div class="bubble ai">CT slot not booked by day 28 <span class="cite">EXAMPLE event</span>. THL: imaging report, biopsy and pathology report each within 1 week {B.C('thl_diagnostic_steps_1wk')}; target is 6 weeks referral → treatment {B.C('thl_6wk_referral_to_treatment')}<div class="meta">{icon('shield')} Simulated patient · rules from THL 21/2016</div></div>
<div class="bubble me">How is Lapland doing on 6-week times today?</div>
<div class="bubble refuse" style="background:transparent;border-color:#6F7D97;color:#A9B4C8"><div class="rl" style="color:#A9B4C8">{icon('eye-off')} No public data</div>No public statistic reports 6-week compliance for any region. That is the gap Tasan Live fills {B.C('nodata_regional_target_compliance')}</div>'''
    body=B.topbar('Tasan Live')+f'''<div class="shell"><main class="main console">
<div class="lhdr"><h1>Tasan Live</h1><div class="ctxl">Lapland · lung pathway<br>navigator console</div><span class="live"><span class="pulse"></span>LIVE</span><span class="badge exd">EXAMPLE · simulated patients</span>
<div class="play"><span class="pb">{icon('pause')}</span><div class="spd"><span>1×</span><span class="on">8×</span><span>32×</span></div><div class="scrub"><div class="bar"><i></i><u style="left:31.1%"></u><b></b></div><div class="lab"><span>Pilot day <b>28</b></span><span>stop/go D90</span></div></div></div></div>
<div class="lgrid">
 <div class="kpirow">
  <div class="dk"><div class="l">Active patients</div><div class="v">14</div>{spark([9,10,12,11,13,14],'#5CC4C4')}<div class="s"><span class="up">▲ 3</span> this week</div></div>
  <div class="dk"><div class="l">On track for 6 weeks</div><div class="v">9<small>/14</small></div>{spark([5,6,6,7,8,9],'#4CC2A4')}<div class="s"><span class="up">▲ 2</span> vs last week</div></div>
  <div class="dk"><div class="l">Day-28 alerts open</div><div class="v" style="color:#F2A65A">3</div>{spark([1,2,1,3,2,3],'#F2A65A')}<div class="s"><span class="am">2 unassigned</span></div></div>
  <div class="dk"><div class="l">Median days, referral → treatment</div><div class="v">33<small>d</small></div>{spark([41,39,38,36,35,33],'#5CC4C4')}<div class="s"><span class="up">▼ 8 d</span> since week 1</div></div>
 </div>
 <div class="dcard ptab"><div class="hd"><h3>{icon('users')}Patients on the clock</h3><span class="mut">sorted by risk · 11 of 14</span></div>
  <table><thead><tr><th></th><th>Patient</th><th>Day</th><th>Pathway step</th><th>Blocker</th><th>Navigator</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>
 <div class="acol">
  <div class="dcard"><div class="hd"><h3>{icon('alert')}Day-28 alert</h3><span class="mut">09:42:07</span></div>
   <div class="focus">{ring(28,128,11,True)}<div><div class="who">P-0207</div><div class="why">Referral D0 · imaging<br>CT slot not booked</div></div></div>
   <div class="acts"><span class="btn pri">{icon('user-plus')}Assign navigator</span><span class="btn gh">{icon('scan')}Request CT slot</span></div></div>
  <div class="dcard" style="flex:1"><div class="hd"><h3>{icon('clock')}Alert queue</h3><span class="mut">3 open</span></div>{arows}</div>
 </div>
 <div class="dcard blocks" style="grid-column:1;grid-row:3"><div class="dcard"><div class="hd"><h3>{icon('alert')}Blockers now</h3><span class="mut">EXAMPLE · patients</span></div>{hbs}</div>
  <div class="dcard"><div class="hd"><h3>{icon('activity')}Treated within 6 weeks</h3><span class="mut">EXAMPLE · weekly %</span></div>{trend.replace(f'width="420"','width="100%"')}</div></div>
 <div class="dcard" style="grid-column:2;grid-row:3"><div class="hd"><h3>{icon('route')}Where time is lost</h3><span class="mut">EXAMPLE · median days</span></div>
  {''.join(f'<div class="hb"><span>{icon(ic)}{n}</span><div class="bt"><i style="width:{v/14*100}%;background:{c}"></i></div><b>{v}</b></div>' for n,ic,v,c in [('Referral→CT','scan',6,'#5CC4C4'),('CT→biopsy','micro',9,'#E6C25A'),('Biopsy→MDT','users',11,'#F2A65A'),('MDT→treatment','activity',7,'#5CC4C4')])}
  <div class="mut" style="margin-top:12px;line-height:1.5">THL: imaging, biopsy, pathology report each ≤ 1 week · <span style="color:#5CC4C4">thl_diagnostic_steps_1wk</span></div></div>
 <div class="dcard feed"><div class="hd"><h3><span class="pulse" style="margin-right:4px"></span>Event feed</h3><span class="mut">EXAMPLE</span></div>{evs}</div>
</div></main>
{B.panel('Lapland · Tasan Live', msgs, ['Summarise today’s alerts','Who needs a navigator?','Draft weekly CMO note'], dark=True)}</div>'''
    open('live.html','w').write(B.page('Tasan mockup – Tasan Live','live.css',body))
