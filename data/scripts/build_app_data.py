"""Chart-ready JSON for the Tasan app (data/app/*.json). Reads ONLY data/csv/*.csv, data/hero.json, data/facts.json (read-only).
Every value carries measure_type and fact_ids (from facts.json, auto-linked through facts' `checks`) or source_url + source_table.
Validate with scripts/check_app_data.py."""
import csv, json, os, math
D=os.path.join(os.path.dirname(__file__),'..'); A=f'{D}/app'; os.makedirs(A,exist_ok=True)
R24='https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf'; R26='https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html'
SOT='https://sotkanet.fi/sotkanet/en/metadata/indicators/'; SF='https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/ksyyt/13u5.px'
FACTS=json.load(open(f'{D}/facts.json'))['facts']; HERO=json.load(open(f'{D}/hero.json'))
FIDX={}
for f in FACTS:
    for c in f.get('checks',[]):
        if 'csv' in c: FIDX.setdefault((c['csv'],tuple(sorted((k,str(v)) for k,v in c['where'].items())),c['col']),[]).append(f['id'])
def fids(csvn,col,**w):
    """fact ids whose checks point at exactly this csv cell (or the same row for any column)"""
    key=tuple(sorted((k,str(v)) for k,v in w.items()))
    out=FIDX.get((csvn,key,col),[])
    if not out: out=sorted({i for (c,k,_),ids in FIDX.items() if c==csvn and k==key for i in ids})
    return sorted(set(out))
cache={}
def rows(n,**w):
    if n not in cache: cache[n]=list(csv.DictReader(open(f'{D}/csv/{n}.csv',encoding='utf-8')))
    return [r for r in cache[n] if all(r.get(k)==str(v) for k,v in w.items())]
def one(n,**w):
    L=rows(n,**w); assert len(L)==1,(n,w,len(L)); return L[0]
def fl(x):
    try: return float(x)
    except: return None
def src(csvn,table,url,mtype,fact_ids=None,**w):
    return {'measure_type':mtype,'fact_ids':fact_ids if fact_ids is not None else [],'source_url':url,'source_table':table,'csv':f'csv/{csvn}.csv' if csvn else None}
def dump(name,obj):
    json.dump(obj,open(f'{A}/{name}','w'),ensure_ascii=False,separators=(',',':')); print(name,os.path.getsize(f'{A}/{name}'),'bytes')
YTA_EN={'Etelä-Suomen yhteistyöalue':('YTA-ETELA','South Finland'),'Itä-Suomen yhteistyöalue':('YTA-ITA','East Finland'),'Länsi-Suomen yhteistyöalue':('YTA-LANSI','West Finland'),'Pohjois-Suomen yhteistyöalue':('YTA-POHJOIS','North Finland'),'Sisä-Suomen yhteistyöalue':('YTA-SISA','Inland Finland')}
YTA_SHORT={'YTA-ETELA':'Etelä-Suomi','YTA-ITA':'Itä-Suomi','YTA-LANSI':'Länsi-Suomi','YTA-POHJOIS':'Pohjois-Suomi','YTA-SISA':'Sisä-Suomi'}
T11='lung_report2026_treatment_by_wsc'; T10='lung_report2026_treatment_by_yta'; AS='lung_report2026_curative_agestd_by_sex_chart_estimate'
AN='lung_report2026_curative_agestd_national_chart_estimate'; SM='lung_report2026_stage_missing_by_wsc_chart_estimate'
T41='lung_report2024_days_dx_to_first_treatment_by_yta'; T45='lung_report2024_first_event_cumulative_by_yta'; T51='lung_report2024_survival_1y_by_yta'
DV='lung_derived_first_active_treatment_by_month_yta'; CS='sotkanet_6103_screening_colorectal_attendance'
TAB11='Keuhkosyöpä Suomessa 2019-2023 (publ. 23.4.2026), Taulukko 11'
CAV_CRUDE='Crude share of all lung cancers diagnosed 2019-2023 among county residents with surgery or curative radiotherapy recorded within 12 months; not stage-adjusted (stage missing 47.7%); depends on treatment recording.'
CAV_YTA='AREA-LEVEL (collaborative area, YTA), not county: same value for every county in the area; older cohort (dx 1/2018-6/2022).'
nat=one(T10,region_code='358',treatment_group_fi='Parantava')
# ---------- 1) counties.json
cur=[r for r in rows(T11,treatment_group_fi='Parantava') if r['region_type']=='HYVINVOINTIALUE']
vals=sorted([fl(r['value']) for r in cur],reverse=True)
pn={c['code']:c for c in HERO['people_number']['counties']}
counties=[]
for r in cur:
    code=r['region_code']; v=fl(r['value']); rank=1+sum(1 for x in vals if x>v); ties=vals.count(v)>1
    ycode,yen=YTA_EN[r['collaborative_area_fi']]
    rec=dict(region=r['region'],region_name_fi=r['region_name_fi'],region_code=code,yta_code=ycode,yta_name=yen,
        curative_crude_pct=v,curative_n=int(r['numerator']),curative_N=int(r['denominator']),curative_ci95_low=fl(r['ci95_low']),curative_ci95_high=fl(r['ci95_high']),
        curative_rank=rank,curative_rank_tied=ties,curative_rank_of=len(cur),curative_vs_national_pp=round(v-fl(nat['value']),1),
        cases_2019_2023=int(r['denominator']),cases_per_year=round(int(r['denominator'])/5,1))
    src_={}
    src_['curative_crude']=dict(src(T11,TAB11,R26,'published',fids(T11,'value',region_code=code,treatment_group_fi='Parantava')),caveat=CAV_CRUDE,ci_measure_type='computed_by_tasan (Wilson 95% CI)')
    src_['curative_rank']=dict(src(T11,TAB11+' (ranked by Tasan; standard competition ranking, ties share the best rank)',R26,'computed_by_tasan'))
    src_['curative_vs_national_pp']=dict(src(T10,'Taulukko 10/11 (difference computed by Tasan)',R26,'computed_by_tasan',fids(T10,'value',region_code='358',treatment_group_fi='Parantava')))
    src_['cases']=dict(src(T11,TAB11+' (denominator; per-year = 5-year total / 5, computed by Tasan)',R26,'published'),note='cases_per_year is computed_by_tasan')
    for sex,key in (('male','men'),('female','women')):
        L=rows(AS,region_code=code,sex=sex)
        if L:
            a=L[0]; rec[f'curative_agestd_{key}_pct']=fl(a['value']); rec[f'curative_agestd_{key}_ci95_low']=fl(a['ci95_low']); rec[f'curative_agestd_{key}_ci95_high']=fl(a['ci95_high'])
            src_[f'curative_agestd_{key}']=dict(src(AS,a['source_table'],R26,'chart_estimate',fids(AS,'value',region_code=code,sex=sex)),caveat='Read by Tasan from Kuva 16 pixels (+/-1 pp); age-standardised, not stage-adjusted.')
        else:
            rec[f'curative_agestd_{key}_pct']=None; rec[f'curative_agestd_{key}_ci95_low']=None; rec[f'curative_agestd_{key}_ci95_high']=None
            src_[f'curative_agestd_{key}']=dict(src(None,'Keuhkosyöpä Suomessa 2019-2023, Kuva 16',R26,'no_public_data'),null_reason='No point drawn for this county in the report figure (suppressed, small numbers).')
    s=rows(SM,region_code=code)
    rec['stage_missing_pct']=fl(s[0]['value']) if s else None
    src_['stage_missing']=dict(src(SM,'Keuhkosyöpä Suomessa 2019-2023, Kuva 13',R26,'chart_estimate',fids(SM,'value',region_code=code)),caveat='Read from chart by Tasan (+/-1 pp).') if s else dict(src(None,'Kuva 13',R26,'no_public_data'),null_reason='not in figure')
    p=pn.get(code)
    rec['people_gap_per_year']=p['gap_per_year'] if p else 0.0
    src_['people_gap_per_year']=dict(src(None,HERO['people_number']['source_table']+'; arithmetic in hero.json people_number (scripts/hero_people_number.py)',R26,'computed_by_tasan',
        ['people_number_lapland'] if code=='21' else ['people_number_national']),caveat=HERO['people_number']['caveat'] if p else 'County at or above national share: no gap counted.')
    # YTA-level linked values
    ys=YTA_SHORT[ycode]
    sv=one(T51,region_code=ycode,sex='total'); sg=one(T41,region_code=ycode,treatment_fi='Leikkaushoito'); t2=one(DV,region_code=ycode,month='2')
    rec.update(yta_level_flag='area-level, not county',yta_surv1y_pct=fl(sv['value']),yta_surv1y_ci95_low=fl(sv['ci95_low']),yta_surv1y_ci95_high=fl(sv['ci95_high']),
        yta_dx_to_surgery_median_days=fl(sg['value']),yta_dx_to_surgery_q1=fl(sg['q1']),yta_dx_to_surgery_q3=fl(sg['q3']),yta_treated_within_2m_pct=fl(t2['value']))
    src_['yta_surv1y']=dict(src(T51,sv['source_table'],R24,'published',fids(T51,'value',region_code=ycode,sex='total')),caveat=CAV_YTA+' 1-year survival, follow-up 2020-2022.')
    src_['yta_dx_to_surgery']=dict(src(T41,sg['source_table'],R24,'published',fids(T41,'value',region_code=ycode,treatment_fi='Leikkaushoito')),caveat=CAV_YTA+' Surgery-first patients only; lower quartile 0 days = surgery on diagnosis date.')
    src_['yta_treated_within_2m']=dict(src(DV,t2['source_table'],R24,'computed_by_tasan',fids(DV,'value',region_code=ycode,month='2')),caveat=CAV_YTA+' Derived by Tasan from Taulukko 4.5.')
    # Goal 2 block
    g2={}
    for sex,key in (('total','total'),('male','men'),('female','women')):
        L=rows(CS,region_code=code,year='2024',sex=sex); g2[key]=fl(L[0]['value']) if L else None
    rec.update(goal2_colorectal_screening_2024_total_pct=g2['total'],goal2_colorectal_screening_2024_men_pct=g2['men'],goal2_colorectal_screening_2024_women_pct=g2['women'],goal2_screening_target_pct=80)
    src_['goal2_colorectal_screening']=dict(src(CS,'Sotkanet 6103 (2024)',SOT+'6103','published',fids(CS,'value',region_code=code,year='2024',sex='total')),goal_link='Goal 2 context (strategy p.5) - NOT Goal 3',caveat='Rollout years; changing age band.')
    rec['src']=src_; counties.append(rec)
counties.sort(key=lambda r:(r['curative_rank'],r['region']))
national=dict(region='Finland',region_code='358',curative_crude_pct=fl(nat['value']),curative_n=int(nat['numerator']),curative_N=int(nat['denominator']),curative_ci95_low=fl(nat['ci95_low']),curative_ci95_high=fl(nat['ci95_high']),
    cases_per_year=round(int(nat['denominator'])/5,1),people_gap_per_year_total=HERO['people_number']['value_per_year'],
    src={'curative_crude':src(T10,'Keuhkosyöpä Suomessa 2019-2023, Taulukko 10 (Koko maa)',R26,'published',fids(T10,'value',region_code='358',treatment_group_fi='Parantava')),
         'people_gap_per_year_total':dict(src(None,'hero.json people_number',R26,'computed_by_tasan',['people_number_national']),caveat=HERO['people_number']['caveat'])})
dump('counties.json',{'generated':'2026-11-14','note':'One record per wellbeing county (21 + Helsinki; Åland not in source). Flat values; src.<field> gives measure_type, fact_ids, source. yta_* fields are AREA-LEVEL, not county.','national':national,'counties':counties})
# ---------- curative_agestd_ranked.json
ranked=[]
for sex,key in (('male','men'),('female','women')):
    L=[r for r in rows(AS,sex=sex) if r['region_type']=='HYVINVOINTIALUE']
    vs=sorted([fl(r['value']) for r in L],reverse=True)
    for r in L:
        v=fl(r['value'])
        ranked.append(dict(sex=key,region=r['region'],region_code=r['region_code'],level='county',value_pct=v,ci95_low=fl(r['ci95_low']),ci95_high=fl(r['ci95_high']),
            rank=1+sum(1 for x in vs if x>v),rank_of=len(L),measure_type='chart_estimate',fact_ids=fids(AS,'value',region_code=r['region_code'],sex=sex),source_url=R26,source_table=r['source_table']))
    ranked.append(dict(sex=key,region='Kainuu wellbeing services county',region_code='20',level='county',value_pct=None,ci95_low=None,ci95_high=None,rank=None,rank_of=len(L),measure_type='no_public_data',fact_ids=[],source_url=R26,source_table='Keuhkosyöpä Suomessa 2019-2023, Kuva 16',null_reason='No point drawn for Kainuu in Kuva 16 (suppressed, small numbers); cannot be digitised.'))
    for r in [x for x in rows(AS,sex=sex) if x['region_type']=='YTA']:
        ranked.append(dict(sex=key,region=r['region'],region_code=r['region_code'],level='yta',value_pct=fl(r['value']),ci95_low=fl(r['ci95_low']),ci95_high=fl(r['ci95_high']),rank=None,rank_of=None,measure_type='chart_estimate',fact_ids=[],source_url=R26,source_table=r['source_table']))
    for r in rows(AN,sex=sex):
        ranked.append(dict(sex=key,region='Finland',region_code='358',level='national_reference_'+('sex_specific' if r['figure']=='Kuva 15' else 'figure16_line'),value_pct=fl(r['value']),ci95_low=None,ci95_high=None,rank=None,rank_of=None,
            measure_type='chart_estimate',fact_ids=[],source_url=R26,source_table=r['source_table'],note=r['interpretation']))
dump('curative_agestd_ranked.json',{'generated':'2026-11-14',
  'method':'All values read by Tasan from pixel positions in report figures (Kuva 16 by county, Kuva 15 by collaborative area): x-axis calibrated on the printed tick marks, point = centre of the dot, CI = ends of the drawn bar, about +/-1 percentage point (scripts/digitise_lung2026_agestd_curative.py, scripts/digitise_lung2026_agestd_national.py). 21 of 22 counties have points; Kainuu is suppressed in the figure. National: use the sex-specific Kuva 15 reference line (men about 24.9, women about 30.0); the Kuva 16 dashed line sits at about 27 in both sex panels (matches crude 27.0%).',
  'caveat':'Age-standardised, NOT stage-adjusted; chart estimates, not published numbers; say "about".','records':ranked})
# ---------- 3) yta.json
yta={'generated':'2026-11-14','note':'AREA-LEVEL (5 collaborative areas, YTA) records; residents; Åland excluded.','membership':[],'timing_medians':[],'first_event_curves':[],'treated_by_month':[],'survival_1y':[],'curative_crude':[],'curative_agestd':[]}
for c in counties: yta['membership'].append(dict(region_code=c['region_code'],region=c['region'],yta_code=c['yta_code'],yta_name=c['yta_name'],source_url=R26,source_table=TAB11+' (Yhteistyöalue column)',measure_type='published',note='Grouping as printed in R2026; R2024 tables use the same five area names (county-by-county mapping not printed in R2024).'))
for r in rows(T41):
    yta['timing_medians'].append(dict(yta_code=r['region_code'],yta_name=r['region_name_fi'],treatment=r['treatment_fi'],median_days=fl(r['value']),q1_days=fl(r['q1']),q3_days=fl(r['q3']),years='diagnosed 1/2018-6/2022',
        measure_type='published',fact_ids=fids(T41,'value',region_code=r['region_code'],treatment_fi=r['treatment_fi']),source_url=R24,source_table=r['source_table'],caveat=r['caveat']))
for r in rows(T45):
    yta['first_event_curves'].append(dict(yta_code=r['region_code'],yta_name=r['region_name_fi'],month=int(r['month']),event=r['event_fi'],cumulative_pct=fl(r['value']),measure_type='published',
        fact_ids=fids(T45,'value',region_code=r['region_code'],month=r['month'],event_fi=r['event_fi']),source_url=R24,source_table=r['source_table']))
for r in rows(DV):
    yta['treated_by_month'].append(dict(yta_code=r['region_code'],yta_name=r['region_name_fi'],month=int(r['month']),treated_pct=fl(r['value']),ci95_low=fl(r['ci95_low']),ci95_high=fl(r['ci95_high']),
        measure_type='computed_by_tasan',fact_ids=fids(DV,'value',region_code=r['region_code'],month=r['month']),source_url=R24,source_table=r['source_table'],caveat='Derived by Tasan (sum of first-event columns); approximate CI.'))
for r in rows(T51):
    yta['survival_1y'].append(dict(yta_code=r['region_code'],yta_name=r['region_name_fi'],sex=r['sex'],surv1y_pct=fl(r['value']),ci95_low=fl(r['ci95_low']),ci95_high=fl(r['ci95_high']),years='follow-up 2020-2022',
        measure_type='published',fact_ids=fids(T51,'value',region_code=r['region_code'],sex=r['sex']),source_url=R24,source_table=r['source_table']))
for r in rows(T10,treatment_group_fi='Parantava'):
    yta['curative_crude'].append(dict(yta_code=r['region_code'],yta_name=r['region_name_fi'],curative_pct=fl(r['value']),n=int(r['numerator']),N=int(r['denominator']),ci95_low=fl(r['ci95_low']),ci95_high=fl(r['ci95_high']),
        measure_type='published',fact_ids=fids(T10,'value',region_code=r['region_code'],treatment_group_fi='Parantava'),source_url=R26,source_table=r['source_table'],ci_measure_type='computed_by_tasan (Wilson)'))
for r in rows(AS,region_type='YTA'):
    yta['curative_agestd'].append(dict(yta_code=r['region_code'],yta_name=r['region_name_fi'],sex=r['sex'],value_pct=fl(r['value']),ci95_low=fl(r['ci95_low']),ci95_high=fl(r['ci95_high']),measure_type='chart_estimate',fact_ids=[],source_url=R26,source_table=r['source_table']))
dump('yta.json',yta)
# ---------- 2) pathway.json
def fact(i): return next(f for f in FACTS if f['id']==i)
def tgt(fid,label,value,unit,clock,status): f=fact(fid); return dict(label=label,value=value,unit=unit,clock_start=clock,status=status,fact_id=fid,source_url=f['source_url'],source_table=f['source_table'])
ref13=[dict(area=r['region'],area_code=r['region_code'],value=fl(r['value'])) for r in rows('sotkanet_13_esh_referrals_processed_within_3d',year='2025',sex='total')]
steps=[
 dict(order=1,id='symptoms_primary_care',label_en='Symptoms / primary care',label_fi='Oireet / perusterveydenhuolto',targets=[],public_data=False,no_public_data=True,
      best_metric=None,null_reason='No cancer-specific primary-care data. Sotkanet 6411 (all-cause GP waits) is excluded: not cancer-specific, Avohilmo gaps in Vantaa, Kerava, Helsinki.',fact_ids=[]),
 dict(order=2,id='referral',label_en='Referral to specialist care',label_fi='Lähete erikoissairaanhoitoon',targets=[tgt('thl_6wk_referral_to_treatment','Referral arrival -> first treatment (clock starts here)',6,'weeks','referral arrival','verified verbatim')],
      public_data=True,no_public_data=False,cancer_specific=False,
      best_metric=dict(name='Referrals processed within 3 days, % (all specialties, not cancer)',level='producer (wellbeing county); 4 Uusimaa counties missing',years='2025',measure_type='published',source_url=SOT+'13',source_table='Sotkanet 13',values=ref13,caveat='Not cancer-specific; producer-based; HUS reports for Uusimaa.'),
      fact_ids=['nodata_referral_to_diagnosis']),
 dict(order=3,id='diagnosis',label_en='Diagnosis (imaging, biopsy, pathology)',label_fi='Diagnostiikka (kuvantaminen, näyte, patologia)',
      targets=[tgt('thl_diagnostic_steps_1wk','Imaging report',1,'week','imaging request','verified verbatim'),tgt('thl_diagnostic_steps_1wk','Biopsy taken',1,'week','request arrives at unit','verified verbatim'),tgt('thl_diagnostic_steps_1wk','Pathology report',1,'week','sampling','verified verbatim')],
      public_data=False,no_public_data=True,
      best_metric=dict(name='Stage information missing at diagnosis, % (data quality, not timing)',level='national (published) + county (chart estimate)',years='diagnosed 2019-2023',measure_type='published',source_url=R26,source_table='Taulukko 4; Kuva 13',
        values=[dict(area='Finland',area_code='358',value=fact('lung_stage_missing_national')['value'],measure_type='published',fact_id='lung_stage_missing_national')]+[dict(area=r['region'],area_code=r['region_code'],value=fl(r['value']),measure_type='chart_estimate',fact_ids=fids(SM,'value',region_code=r['region_code'])) for r in rows(SM)]),
      null_reason='No public time-to-diagnosis or diagnostic-step times for lung cancer at any level.',fact_ids=['nodata_referral_to_diagnosis','lung_stage_missing_national','nodata_stage_adjusted_comparison']),
 dict(order=4,id='mdt',label_en='MDT decision',label_fi='Moniammatillinen hoitokokous (MDT)',targets=[],public_data=True,no_public_data=False,
      best_metric=dict(name='MDT meeting coded within 12 months, % (coding practice, not MDT frequency)',level='collaborative area (YTA)',years='diagnosed 2019-2023',measure_type='published',source_url=R26,source_table='Taulukko 10',
        values=[dict(area=r['region_name_fi'],area_code=r['region_code'],value=fl(r['value']),n=int(r['numerator']),N=int(r['denominator'])) for r in rows(T10,treatment_group_fi='MDT-käsittely')],caveat='Only Inland Finland codes MDT systematically.'),
      null_reason='No THL target time for MDT.',fact_ids=['lung_mdt_coding_inland_only']),
 dict(order=5,id='treatment_start',label_en='First treatment',label_fi='Ensimmäinen hoito',
      targets=[tgt('thl_6wk_referral_to_treatment','Referral -> first treatment (all cancers incl. lung)',6,'weeks','referral arrival','verified verbatim'),tgt('thl_very_urgent_2_3wk','Very urgent cancers',3,'weeks (max; few days to 2-3 wk)','diagnosis','verified verbatim'),
               tgt('thl_breast_4wk','Breast: queue -> surgery / neoadjuvant drug',4,'weeks','queue placement','diagram (primary source only)'),tgt('thl_colorectal_3wk','Colon/rectum: queue -> first treatment',3,'weeks','queue placement','diagram (primary source only)'),
               tgt('thl_prostate_6wk_4wk','Prostate: queue -> surveillance/surgery/RT (drug 4 wk)',6,'weeks','queue placement','diagram (primary source only)'),
               dict(label='Lung: no lung-specific target (generic 6 weeks applies)',value=None,unit=None,clock_start=None,status='verified absent',fact_id='thl_no_lung_specific_target',source_url=fact('thl_no_lung_specific_target')['source_url'],source_table=fact('thl_no_lung_specific_target')['source_table'])],
      public_data=True,no_public_data=False,
      best_metric=dict(name='Median days diagnosis -> surgery (surgery-first patients)',level='collaborative area (YTA)',years='diagnosed 1/2018-6/2022',measure_type='published',source_url=R24,source_table='Taulukko 4.1, PDF p.28',
        values=[dict(area=r['region_name_fi'],area_code=r['region_code'],value=fl(r['value']),q1=fl(r['q1']),q3=fl(r['q3'])) for r in rows(T41,treatment_fi='Leikkaushoito')],caveat='Starts at diagnosis, not referral; lower quartile 0 days in 3 areas.'),
      secondary_metric=dict(name='Share of all patients with first active treatment within 2 months, %',level='collaborative area (YTA)',measure_type='computed_by_tasan',source_url=R24,source_table='Taulukko 4.5 (derived)',
        values=[dict(area=r['region_name_fi'],area_code=r['region_code'],value=fl(r['value'])) for r in rows(DV,month='2')]),
      null_reason='No public compliance with the 6-week target, and no county-level times.',fact_ids=['lung_dx_to_surgery_north','lung_dx_to_surgery_south','lung_same_day_surgery_caveat','lung_treated_2m_inland','lung_treated_2m_west','nodata_regional_target_compliance','nodata_dx_to_treatment_by_county']),
 dict(order=6,id='follow_on_treatment',label_en='Follow-on (adjuvant) treatment',label_fi='Liitännäishoito',
      targets=[tgt('thl_adjuvant_4wk','Surgery -> adjuvant radio/drug therapy',4,'weeks','surgery','verified verbatim')],public_data=False,no_public_data=True,best_metric=None,
      null_reason='No public regional data on time from surgery to adjuvant treatment for lung cancer.',fact_ids=[]),
]
goal3=[dict(id=i,statement_en=fact(i)['statement_en'],statement_fi=fact(i)['statement_fi'],source_url=fact(i)['source_url'],source_table=fact(i)['source_table']) for i in ('g3_indicator_survival','g3_indicator_mortality','g3_indicator_target_times')]
dump('pathway.json',{'generated':'2026-11-14','goal3_indicators':goal3,'steps':steps,'note':'THL Ohjaus 21/2016 is watermarked "Vanhentunut" (outdated) but is the document the strategy cites.'})
# ---------- pathway_by_county.json
pbc=[]
r13={r['region_code']:fl(r['value']) for r in rows('sotkanet_13_esh_referrals_processed_within_3d',year='2025',sex='total')}
for c in counties:
    code=c['region_code']; rv=r13.get(code)
    pbc.append(dict(region=c['region'],region_code=code,yta_code=c['yta_code'],
      referral_value=rv,referral_metric='Referrals processed within 3 days, % (all specialties, producer-based; not cancer-specific)',referral_level='county (producer)',referral_measure_type='published' if rv is not None else 'no_public_data',
      referral_source=dict(source_url=SOT+'13',source_table='Sotkanet 13 (2025)'),referral_null_reason=None if rv is not None else 'Not reported for this county in 2025 (HUS reports for Uusimaa). No cancer-specific referral data exist anywhere.',
      diagnosis_value=None,diagnosis_null_reason='No public time-to-diagnosis data for lung cancer at any level (fact nodata_referral_to_diagnosis).',diagnosis_fact_ids=['nodata_referral_to_diagnosis'],
      diagnosis_stage_missing_pct=c['stage_missing_pct'],diagnosis_stage_missing_measure_type='chart_estimate',diagnosis_stage_missing_source=dict(source_url=R26,source_table='Kuva 13'),
      treatment_start_value=None,treatment_start_null_reason='Not published by county; only by collaborative area (fact nodata_dx_to_treatment_by_county).',
      treatment_start_yta_dx_to_surgery_median_days=c['yta_dx_to_surgery_median_days'],treatment_start_yta_treated_within_2m_pct=c['yta_treated_within_2m_pct'],treatment_start_yta_flag='YTA-level, not county',
      treatment_start_fact_ids=c['src']['yta_dx_to_surgery']['fact_ids']+c['src']['yta_treated_within_2m']['fact_ids']+['nodata_dx_to_treatment_by_county'],
      curative_share_pct=c['curative_crude_pct'],curative_ci95_low=c['curative_ci95_low'],curative_ci95_high=c['curative_ci95_high'],curative_measure_type='published',curative_fact_ids=c['src']['curative_crude']['fact_ids'],curative_source=dict(source_url=R26,source_table=TAB11),
      target_compliance_value=None,target_compliance_null_reason='No region publishes 6-week compliance (fact nodata_regional_target_compliance).'))
dump('pathway_by_county.json',{'generated':'2026-11-14','records':pbc})
# ---------- timeseries.json
ts=[]
def add(sid,region,code,year,value,unit,mtype,url,table,fact_ids=None,sex='total',caveat=''):
    ts.append(dict(series_id=sid,region=region,region_code=code,sex=sex,year=year,value=value,unit=unit,measure_type=mtype,fact_ids=fact_ids or [],source_url=url,source_table=table,caveat=caveat))
for r in rows(CS):
    if r['region_type'] in ('HYVINVOINTIALUE','MAA'):
        add('colorectal_screening_attendance',r['region'],r['region_code'],int(r['year']),fl(r['value']),'%','published',SOT+'6103','Sotkanet 6103',fids(CS,'value',region_code=r['region_code'],year=r['year'],sex=r['sex']),sex=r['sex'],caveat='Goal 2 context; rollout years 2022-2024.')
for r in rows('sotkanet_3621_screening_breast_attendance'):
    if r['region_type'] in ('HYVINVOINTIALUE','MAA'):
        add('breast_screening_attendance',r['region'],r['region_code'],int(r['year']),fl(r['value']),'%','published',SOT+'3621','Sotkanet 3621',fids('sotkanet_3621_screening_breast_attendance','value',region_code=r['region_code'],year=r['year'],sex='total'),caveat='Goal 2 context.')
for r in rows('sotkanet_3627_survival5y_bowel'):
    if r['region_type'] in ('HYVINVOINTIALUE','MAA'):
        add('bowel_survival_5y',r['region'],r['region_code'],int(r['year']),fl(r['value']),'%','published',SOT+'3627','Sotkanet 3627',fids('sotkanet_3627_survival5y_bowel','value',region_code=r['region_code'],year=r['year']),caveat='Statistical year = 10 pooled diagnosis years; age-standardised; no 2018 value in source.')
for r in rows('statfin_13u5_cancer_deaths_by_wsc',region_code='SSS'):
    sid={'Deaths by underlying cause: 04-21 Syövät (C00-C97)':'cancer_deaths_all','Deaths by underlying cause: 11 Kurkunpään, henkitorven ja keuhkon syöpä (C32-C34)':'lung_larynx_deaths'}.get(r['indicator'])
    if sid: add(sid,'Finland','358',int(r['year']),int(r['deaths']),'deaths','published',SF,'StatFin 13u5',fids('statfin_13u5_cancer_deaths_by_wsc','deaths',region_code='SSS',year=r['year'],indicator=r['indicator']),caveat='C32-C34 includes larynx.' if sid=='lung_larynx_deaths' else '')
for r in rows('statfin_13u5_cancer_deaths_by_wsc',indicator='Deaths by underlying cause: 04-21 Syövät (C00-C97)'):
    if r['region_code'].startswith('HVA') and r['region_code']!='HVA91':
        add('cancer_deaths_all_by_county',r['region'],r['region_code'].replace('HVA',''),int(r['year']),int(r['deaths']),'deaths','published',SF,'StatFin 13u5',caveat='Counts only; county comparisons confounded by population size and age; do not rank.')
for r in rows('lung_report2026_national_by_year'):
    sid={'New lung cancer patients (C33-C34), by year of follow-up start':'lung_new_patients','Patients with a lung cancer treatment procedure recorded within 12 months':'lung_procedure_recorded_pct','Patients with an MDT meeting recorded within 12 months':'lung_mdt_recorded_pct','Patients who died within 12 months':'lung_died_12m_pct'}[r['indicator']]
    v=int(r['value']) if sid=='lung_new_patients' else fl(r['pct'])
    add(sid,'Finland','358',int(r['year']),v,'patients' if sid=='lung_new_patients' else '%','published',R26,r['source_table'],caveat='Year = year of follow-up start (registry diagnosis date or a lung-cancer hospital visit up to 3 months earlier).')
dump('timeseries.json',{'generated':'2026-11-14','series':sorted({t['series_id'] for t in ts}),'records':ts})
