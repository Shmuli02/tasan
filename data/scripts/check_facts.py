"""Validate data/facts.json: JSON, unique ids, required fields, allowed enums, source_url present,
numbers in statement text, and every `checks` pointer re-read from data/csv/*.csv, data/hero.json, or raw text. Exit 1 on any failure."""
import json, csv, os, re, sys
D=os.path.join(os.path.dirname(__file__),'..')
fx=json.load(open(f'{D}/facts.json')); facts=fx['facts']; err=[]; ok=0
REQ=['id','statement_fi','statement_en','value','unit','region','years','pathway_stage','goal_link','source_url','source_table','measure_type','caveat']
STAGES={'detection','referral','diagnosis','treatment_start','treatment','outcome','data_gap','policy'}
TYPES={'published','computed_by_tasan','chart_estimate','no_public_data'}
ids=[f['id'] for f in facts]
dups={i for i in ids if ids.count(i)>1}
if dups: err.append(f'duplicate ids {dups}')
if not fx.get('usage_rules'): err.append('missing usage_rules')
cache={}
def load(n):
    if n not in cache: cache[n]=list(csv.DictReader(open(f'{D}/csv/{n}.csv',encoding='utf-8')))
    return cache[n]
def num(x):
    try: return float(x)
    except: return None
# text evidence for numbers that come from report prose (not a CSV)
TEXT={'lung_dx_to_surgery_national':('raw/Keuhkosyopa_Suomessa.txt',r'leikatuilla 37 päivää \(kvartiiliväli 0 – 56\), sädehoidetuilla 36 päivää \(16 – 56\)'),
 'lung_any_surgery_national':('raw/Keuhkosyopa_Suomessa.txt',r'joka kymmenes potilas \(N 1627\)'),
 'lung_localised_share':('raw/keuhkosyoparaportti_2026.txt',r'5 % kaikista potilaista ja 11 % niistä'),
 'lung_no_record_died_79':('raw/keuhkosyoparaportti_2026.txt',r'Suurin osa \(79 %\) näistä potilaista kuoli'),
 'g3_indicator_mortality':('raw/Kansallinen_syopastrategia_2026_2035_FINAL.txt',r'Syöpäkuolleisuus pienenee 10 % \(nykyisin 13 300 henkilöä vuodessa\)'),
 'g3_indicator_survival':('raw/Kansallinen_syopastrategia_2026_2035_FINAL.txt',r'Huonoennusteisten syöpien 5 vuoden elossaololuvut saavuttavat pohjoismaisen'),
 'g3_survival_footnote_lung':('raw/Kansallinen_syopastrategia_2026_2035_FINAL.txt',r'yli 14 prosenttiyksikköä keuhko'),
 'g3_indicator_target_times':('raw/Kansallinen_syopastrategia_2026_2035_FINAL.txt',r'Potilaat pääsevät hoitoon tavoiteaikojen puitteissa'),
 'g2_screening_target':('raw/Kansallinen_syopastrategia_2026_2035_FINAL.txt',r'Kaikissa syöpäseulontaohjelmissa saavutetaan 80 %:n osallistumisaste'),
 'g2_stage_target':('raw/Kansallinen_syopastrategia_2026_2035_FINAL.txt',r'Vähintään 70 % syövistä diagnosoidaan levinneisyysluokissa I'),
 'thl_6wk_referral_to_treatment':('raw/thl_ohjaus_21_2016.txt',r'ensimmäiseen hoitoon \(leikkaus, lääke- tai sädehoito\) on 6 viikkoa'),
 'thl_very_urgent_2_3wk':('raw/thl_ohjaus_21_2016.txt',r'korkeintaan 2−3 viikossa diagnoosista'),
 'thl_adjuvant_4wk':('raw/thl_ohjaus_21_2016.txt',r'viimeistään 4 viikon kuluessa leikkauksesta'),
 'thl_diagnostic_steps_1wk':('raw/thl_ohjaus_21_2016.txt',r'Patologin lausunnon tulee olla käytettävissä viikon kuluessa'),
 'thl_breast_4wk':('raw/thl_ohjaus_21_2016.txt',r'4 vkoa\s+Leikkaus'),
 'thl_colorectal_3wk':('raw/thl_ohjaus_21_2016.txt',r'3 vkoa'),
 'thl_prostate_6wk_4wk':('raw/thl_ohjaus_21_2016.txt',r'Eturauhassyöpä\s+6 vkoa'),
 'thl_no_lung_specific_target':('raw/thl_ohjaus_21_2016.txt',r'paksu- ja peräsuolisyöpä \(C18-20-alkuiset diagnoosit\)'),
 'roadmap_cancer_specific_times_pending':('raw/Kansallinen_syopastrategia_toimeenpanon_tiekartta_2026_2031.txt',r'syöpäkohtaiset hoitoonpääsyajat on määritetty'),
 'g3_goal_title':('raw/Kansallinen_syopastrategia_2026_2035_FINAL.txt',r'Varmistetaan yhdenvertainen ja vaikuttava syövänhoito'),
 'subgoal_32_data_coverage':('raw/Kansallinen_syopastrategia_2026_2035_FINAL.txt',r'tietopohjan kattavuus 90 %'),
}
def norm(t): return re.sub(r'\s+',' ',t.replace('\u00ad','').replace('\u200b',''))
for f in facts:
    fid=f.get('id','?')
    for k in REQ:
        if k not in f: err.append(f'{fid}: missing {k}')
    if f['pathway_stage'] not in STAGES: err.append(f'{fid}: bad stage')
    if f['measure_type'] not in TYPES: err.append(f'{fid}: bad measure_type')
    if not str(f.get('source_url','')).startswith('http'): err.append(f'{fid}: no source_url')
    if f['measure_type']=='no_public_data' and f['value'] is not None: err.append(f'{fid}: no_public_data must have value null')
    gl=f['goal_link'].lower()
    if any(w in fid for w in ('screening','stage_target','stage_distribution','screening_by')) and 'goal 3' in gl and 'not goal 3' not in gl: err.append(f'{fid}: screening/stage labelled Goal 3')
    if f['measure_type'] in ('computed_by_tasan','chart_estimate') and not any('count' in c for c in f.get('checks',[])) and 'about' not in f['statement_en'].lower(): err.append(f'{fid}: computed/chart fact must say "about"')
    v=f['value']
    if isinstance(v,(int,float)):
        txt=f['statement_en'].replace(' ','')  # allow "27 400"
        forms={str(v),f'{v:g}',str(int(v)) if float(v).is_integer() else str(v)}
        if not any(s in txt for s in forms): err.append(f'{fid}: value {v} not in statement_en')
    for c in f.get('checks',[]):
        if 'hero' in c:
            h=json.load(open(f'{D}/hero.json'))
            for part in c['hero'].split('.'): h=h[part]
            if h!=c['expect']: err.append(f'{fid}: hero {c["hero"]}={h} != {c["expect"]}')
            else: ok+=1
            continue
        if 'count' in c:
            L=[r for r in load(c['count']) if all(r.get(k)==w for k,w in c['where'].items())]
            n=sum(1 for r in L if num(r[c['col']])>=c['ge'])
            if n!=c['expect'] or len(L)!=c['expect_total']: err.append(f'{fid}: count {n}/{len(L)} != {c["expect"]}/{c["expect_total"]}')
            else: ok+=1
            continue
        L=[r for r in load(c['csv']) if all(r.get(k)==str(w) for k,w in c['where'].items())]
        if len(L)!=1: err.append(f'{fid}: {c["csv"]} {c["where"]} matched {len(L)} rows'); continue
        got=L[0][c['col']]; exp=c['expect']
        if isinstance(exp,str):
            good=got==exp
        else:
            g=num(got); good=g is not None and abs(g-exp)<=c.get('tol',0.051)
        if good: ok+=1
        else: err.append(f'{fid}: {c["csv"]}.{c["col"]}={got} != {exp}')
    if fid in TEXT:
        fn,rx=TEXT[fid]
        if re.search(rx,norm(open(f'{D}/{fn}',encoding='utf-8',errors='ignore').read())): ok+=1
        else: err.append(f'{fid}: text evidence not found in {fn}')
nochk=[f['id'] for f in facts if f['measure_type']!='no_public_data' and not f.get('checks') and f['id'] not in TEXT]
from collections import Counter
print('facts:',len(facts),'| checks passed:',ok,'| errors:',len(err))
print('by stage:',dict(Counter(f['pathway_stage'] for f in facts)))
print('by type :',dict(Counter(f['measure_type'] for f in facts)))
print('facts without machine check (sourced from MD/report prose):',nochk)
for e in err: print('ERROR',e)
sys.exit(1 if err else 0)
