"""Validate data/app/*.json against data/csv and data/facts.json. Exit 1 on any failure."""
import csv, json, os, sys
D=os.path.join(os.path.dirname(__file__),'..'); A=f'{D}/app'
MT={'published','computed_by_tasan','chart_estimate','no_public_data'}
fails=[]; n=0
def ok(c,msg):
    global n; n+=1
    if not c: fails.append(msg)
def load(f): return json.load(open(f'{A}/{f}'))
def rows(name,**w): return [r for r in csv.DictReader(open(f'{D}/csv/{name}.csv',encoding='utf-8')) if all(r.get(k)==str(v) for k,v in w.items())]
def fl(x):
    try: return float(x)
    except: return None
FACTS={f['id']:f for f in json.load(open(f'{D}/facts.json'))['facts']}
def has_source(d): return bool(d.get('fact_ids') or d.get('fact_id') or (d.get('source_url') and d.get('source_table')))
def fact_ids_exist(d):
    for i in (d.get('fact_ids') or [])+([d['fact_id']] if d.get('fact_id') else []): ok(i in FACTS,f'unknown fact id {i}')
# --- counties.json
c=load('counties.json'); C=c['counties']
ok(len(C)==22,'22 county records'); ok(len({r['region_code'] for r in C})==22,'unique codes')
yta={r['region_code']:r for r in rows('lung_report2026_treatment_by_yta',treatment_group_fi='Parantava')}
for r in C:
    code=r['region_code']; t=rows('lung_report2026_treatment_by_wsc',region_code=code,treatment_group_fi='Parantava')[0]
    ok(r['curative_crude_pct']==fl(t['value']) and r['curative_n']==int(t['numerator']) and r['curative_N']==int(t['denominator']),f'{code} crude vs T11')
    ok(r['curative_ci95_low']==fl(t['ci95_low']) and r['curative_ci95_high']==fl(t['ci95_high']),f'{code} CI')
    ok(r['curative_ci95_low']<=r['curative_crude_pct']<=r['curative_ci95_high'],f'{code} CI brackets value')
    ok(r['curative_rank']==1+sum(1 for x in C if x['curative_crude_pct']>r['curative_crude_pct']),f'{code} rank')
    ok(r['cases_per_year']==round(r['curative_N']/5,1),f'{code} per year')
    for sex,key in (('male','men'),('female','women')):
        a=rows('lung_report2026_curative_agestd_by_sex_chart_estimate',region_code=code,sex=sex)
        ok((r[f'curative_agestd_{key}_pct']==fl(a[0]['value'])) if a else (r[f'curative_agestd_{key}_pct'] is None and r['src'][f'curative_agestd_{key}'].get('null_reason')),f'{code} agestd {key}')
    s=rows('lung_report2026_stage_missing_by_wsc_chart_estimate',region_code=code); ok(s and r['stage_missing_pct']==fl(s[0]['value']),f'{code} stage missing')
    ok(r['yta_level_flag']=='area-level, not county','yta flag')
    y=rows('lung_report2024_survival_1y_by_yta',region_code=r['yta_code'],sex='total')[0]; ok(r['yta_surv1y_pct']==fl(y['value']),f'{code} yta surv')
    g=rows('sotkanet_6103_screening_colorectal_attendance',region_code=code,year='2024',sex='total'); ok(g and r['goal2_colorectal_screening_2024_total_pct']==fl(g[0]['value']),f'{code} screening')
    ok('Goal 2' in r['src']['goal2_colorectal_screening']['goal_link'] and 'NOT Goal 3' in r['src']['goal2_colorectal_screening']['goal_link'],'screening labelled Goal 2')
    for k,sv in r['src'].items():
        ok(sv.get('measure_type') in MT,f'{code} {k} measure_type'); ok(has_source(sv),f'{code} {k} source'); fact_ids_exist(sv)
        if sv.get('measure_type')=='no_public_data': ok(bool(sv.get('null_reason')),f'{code} {k} null reason')
    # linked crude facts must equal value
    for i in r['src']['curative_crude']['fact_ids']: ok(FACTS[i]['value']==r['curative_crude_pct'],f'{i} fact value')
hero=json.load(open(f'{D}/hero.json'))['people_number']
ok(abs(sum(r['people_gap_per_year'] for r in C)-hero['value_per_year'])<2,'people gaps sum ~ hero total (rounding)')
ok(c['national']['curative_crude_pct']==FACTS['lung_curative_national']['value'],'national crude = fact')
# --- curative_agestd_ranked.json
k=load('curative_agestd_ranked.json')
for r in k['records']:
    ok(r['measure_type'] in MT and has_source(r),f"ranked {r['region']} source"); fact_ids_exist(r)
    if r['value_pct'] is None: ok(bool(r.get('null_reason')),'ranked null reason')
    elif r['ci95_low'] is not None: ok(r['ci95_low']<=r['value_pct']<=r['ci95_high'],f"ranked CI {r['region']} {r['sex']}")
    if r['level']=='county' and r['value_pct'] is not None:
        a=rows('lung_report2026_curative_agestd_by_sex_chart_estimate',region_code=r['region_code'],sex={'men':'male','women':'female'}[r['sex']])[0]; ok(r['value_pct']==fl(a['value']),'ranked vs csv')
for sex in ('men','women'):
    ok(sum(1 for r in k['records'] if r['sex']==sex and r['level']=='county')==22,f'22 counties {sex}')
    ok(any(r['sex']==sex and r['level']=='national_reference_sex_specific' for r in k['records']),f'national ref {sex}')
# --- yta.json
y=load('yta.json')
for sec in ('membership','timing_medians','first_event_curves','treated_by_month','survival_1y','curative_crude','curative_agestd'):
    ok(len(y[sec])>0,f'yta {sec} nonempty')
    for r in y[sec]: ok(r.get('measure_type') in MT and has_source(r),f'yta {sec} source'); fact_ids_exist(r)
for r in y['timing_medians']:
    t=rows('lung_report2024_days_dx_to_first_treatment_by_yta',region_code=r['yta_code'],treatment_fi=r['treatment'])[0]; ok(r['median_days']==fl(t['value']) and r['q1_days']==fl(t['q1']),'T4.1 match')
for r in y['first_event_curves']:
    t=rows('lung_report2024_first_event_cumulative_by_yta',region_code=r['yta_code'],month=r['month'],event_fi=r['event'])[0]; ok(r['cumulative_pct']==fl(t['value']),'T4.5 match')
for r in y['survival_1y']:
    for i in r['fact_ids']:
        if isinstance(FACTS[i]['value'],(int,float)) and FACTS[i]['value']==r['surv1y_pct']: pass
# --- pathway.json
p=load('pathway.json'); S=p['steps']
ok([s['order'] for s in S]==list(range(1,7)),'6 ordered steps')
ok([g['id'] for g in p['goal3_indicators']]==['g3_indicator_survival','g3_indicator_mortality','g3_indicator_target_times'],'exactly 3 Goal 3 indicators')
for s in S:
    ok(isinstance(s['public_data'],bool) and s['no_public_data']==(not s['public_data']),f"{s['id']} flags")
    if s['no_public_data'] or s['best_metric'] is None: ok(bool(s.get('null_reason')),f"{s['id']} null reason")
    for t in s['targets']: ok(t['fact_id'] in FACTS and has_source(t),f"{s['id']} target source")
    for m in (s.get('best_metric'),s.get('secondary_metric')):
        if m: ok(m['measure_type'] in MT and has_source(m) and len(m['values'])>0,f"{s['id']} metric source")
    for i in s['fact_ids']: ok(i in FACTS,f'unknown {i}')
lung=[t for s in S for t in s['targets'] if t['fact_id']=='thl_no_lung_specific_target']; ok(len(lung)==1 and lung[0]['value'] is None,'lung has no specific target')
for t in [t for s in S for t in s['targets'] if t['fact_id'] in ('thl_breast_4wk','thl_colorectal_3wk','thl_prostate_6wk_4wk')]: ok('diagram' in t['status'],'diagram targets flagged')
# --- pathway_by_county.json
b=load('pathway_by_county.json')['records']; ok(len(b)==22,'pbc 22')
for r in b:
    for st in ('referral','diagnosis','treatment_start'):
        v=r[f'{st}_value']; ok(v is not None or bool(r[f'{st}_null_reason']),f"{r['region_code']} {st} null reason")
    ok(r['treatment_start_yta_flag']=='YTA-level, not county','pbc yta flag')
    ok(r['curative_share_pct']==next(x['curative_crude_pct'] for x in C if x['region_code']==r['region_code']),'pbc curative')
# --- timeseries.json
T=load('timeseries.json')['records']
ok(len({(r['series_id'],r['region_code'],r['sex'],r['year']) for r in T})==len(T),'timeseries unique keys')
for r in T:
    ok(r['measure_type'] in MT and has_source(r) and r['value'] is not None,f"ts {r['series_id']} source/value"); fact_ids_exist(r)
src={'colorectal_screening_attendance':('sotkanet_6103_screening_colorectal_attendance','value'),'breast_screening_attendance':('sotkanet_3621_screening_breast_attendance','value'),'bowel_survival_5y':('sotkanet_3627_survival5y_bowel','value')}
for r in T:
    if r['series_id'] in src:
        f,col=src[r['series_id']]; m=rows(f,region_code=r['region_code'],year=r['year'],sex=r['sex']); ok(m and fl(m[0][col])==r['value'],f"ts {r['series_id']} {r['region_code']} {r['year']}")
    if r['series_id']=='cancer_deaths_all' and r['year']==2024: ok(r['value']==FACTS['cancer_deaths_2024']['value'],'deaths 2024 = fact')
    if r['series_id']=='lung_larynx_deaths' and r['year']==2024: ok(r['value']==FACTS['lung_deaths_2024']['value'],'lung deaths 2024 = fact')
    for i in r['fact_ids']:
        fv=FACTS[i]['value']
        if isinstance(fv,(int,float)) and r['series_id'] in src and FACTS[i].get('checks') and FACTS[i]['checks'][0].get('col')=='value' and len(FACTS[i]['checks'])==1: ok(fv==r['value'],f'ts fact {i}')
ok(not any('Goal 3' in json.dumps(r) for r in T if 'screening' in r['series_id']),'screening never labelled Goal 3')
print(f'{n} checks, {len(fails)} failures')
for f in fails[:40]: print('FAIL',f)
sys.exit(1 if fails else 0)
