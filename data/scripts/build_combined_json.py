"""Combine every CSV in data/csv into data/combined.json: {file: {rows:[...]}} plus metadata."""
import csv, json, glob, os
D=os.path.join(os.path.dirname(__file__),'..')
out={'generated':'2026-11-14','note':'Public aggregate data only. Every row carries source_url and source_table. See SOURCES.md / FINDINGS.md.','tables':{}}
for f in sorted(glob.glob(f'{D}/csv/*.csv')):
    rows=list(csv.DictReader(open(f,encoding='utf-8')))
    out['tables'][os.path.basename(f)[:-4]]={'n_rows':len(rows),'columns':list(rows[0].keys()) if rows else [],'rows':rows}
json.dump(out,open(f'{D}/combined.json','w'),ensure_ascii=False)
print({k:v['n_rows'] for k,v in out['tables'].items()})
