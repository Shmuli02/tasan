"""Convert raw Sotkanet JSON -> tidy CSVs (wellbeing services counties + whole country).
Columns: region, region_code, region_type, year, sex, indicator_id, indicator, value, abs_value, unit, source_url, source_table"""
import json, csv, glob, os
D=os.path.join(os.path.dirname(__file__),'..'); RAW=f'{D}/raw/sotkanet'
R={r['id']:r for r in json.load(open(f'{D}/raw/sotkanet_regions.json'))}
KEEP={'HYVINVOINTIALUE','MAA'}
SLUG={3620:'screening_cervical_attendance',3621:'screening_breast_attendance',6103:'screening_colorectal_attendance',
 3625:'survival5y_breast',3626:'survival5y_cervical',3627:'survival5y_bowel',5643:'cancer_index_agestd',5644:'cancer_index_crude',
 245:'cancer_index_agestd_old',5093:'kela_cancer_med_refund_agestd',5395:'kela_cancer_med_refund_crude',13:'esh_referrals_processed_within_3d',
 5033:'esh_referrals_processed_over_21d',5073:'esh_referrals_per_1000',3336:'esh_waiting_over_6m_per_10000',5083:'esh_median_wait_dec31',
 6411:'phc_physician_wait_over_7d',6410:'phc_physician_wait_over_3m',2676:'phc_physician_wait_over_7d_march_old',3175:'phc_physician_wait_over_3m_march_old',186:'mortality_all_cause_per_100000'}
allrows=[]
for f in glob.glob(f'{RAW}/*_meta.json'):
    i=int(os.path.basename(f).split('_')[0]); m=json.load(open(f))
    if i not in SLUG: continue
    data=json.load(open(f'{RAW}/{i}.json'))
    keep=KEEP|({'SAIRAANHOITOPIIRI'} if i==5083 else set())
    unit=m.get('primaryValueType',{}).get('title',{}).get('en','')
    src=f"https://sotkanet.fi/sotkanet/en/metadata/indicators/{i}"
    rows=[]
    for x in data:
        r=R.get(x['region'])
        if not r or r['category'] not in keep or x.get('value') is None: continue
        rows.append(dict(region=r['title'].get('en') or r['title']['fi'],region_name_fi=r['title']['fi'],region_code=r['code'],region_type=r['category'],
          year=x['year'],sex=x['gender'],indicator_id=i,indicator=m['title']['en'],value=x['value'],abs_value=x.get('absValue',''),unit=unit,
          source_url=src,source_table=f"THL Sotkanet indicator {i} (REST API https://sotkanet.fi/rest/1.1/json?indicator={i}); data source: "+'; '.join(s['title']['en'] for s in m.get('sources',[]))+f"; data-updated {m.get('data-updated')}"))
    rows.sort(key=lambda r:(r['year'],r['sex'],r['region_code']))
    os.makedirs(f'{D}/csv',exist_ok=True)
    with open(f'{D}/csv/sotkanet_{i}_{SLUG[i]}.csv','w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    allrows+=rows
json.dump(allrows,open(f'{D}/raw/sotkanet_all_tidy.json','w'),ensure_ascii=False,indent=0)
print(len(allrows))
