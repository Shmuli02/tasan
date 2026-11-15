"""Manual transcription (verified against rendered page image raw/lung_figs/lung2024_t41-28.png) of
TAULUKKO 4.1 'Aika päivissä ensimmäiseen hoitotoimenpiteeseen kuuden kuukauden kuluessa diagnoosipäivästä yhteistyöalueittain'
Keuhkosyöpä Suomessa – Katsaus keuhkosyövän hoidon laadusta (Finnish Cancer Registry, Nov 2024), printed p.27 / PDF p.28.
Cohort: lung cancers diagnosed 1.1.2018–30.6.2022 (N=13 324). Interval = Cancer Registry diagnosis date -> first treatment within 6 months."""
import csv, os
D=os.path.join(os.path.dirname(__file__),'..')
T=[('Etelä-Suomi','Leikkaushoito',46.0,33.0,63.0),('Etelä-Suomi','Sädehoito',39.0,18.0,56.0),('Etelä-Suomi','Lääkehoito',36.0,24.0,54.0),
('Itä-Suomi','Leikkaushoito',27.0,0.0,43.5),('Itä-Suomi','Sädehoito',25.0,11.0,47.0),('Itä-Suomi','Lääkehoito',36.0,22.0,56.0),
('Länsi-Suomi','Leikkaushoito',42.0,28.0,55.0),('Länsi-Suomi','Sädehoito',45.0,26.0,74.5),('Länsi-Suomi','Lääkehoito',34.5,23.0,48.2),
('Pohjois-Suomi','Leikkaushoito',13.5,0.0,44.0),('Pohjois-Suomi','Sädehoito',31.0,14.0,54.0),('Pohjois-Suomi','Lääkehoito',42.0,28.2,57.0),
('Sisä-Suomi','Leikkaushoito',29.0,0.0,51.0),('Sisä-Suomi','Sädehoito',40.0,21.0,57.8),('Sisä-Suomi','Lääkehoito',43.0,28.0,61.0)]
EN={'Leikkaushoito':'surgery','Sädehoito':'radiotherapy (excl. palliative)','Lääkehoito':'drug therapy'}
rows=[dict(region=f'{a} yhteistyöalue (collaborative area)',region_code='YTA',year='diagnosed 2018-01-01..2022-06-30',sex='total',
  indicator=f'Lung cancer: days from diagnosis to first {EN[h]} (within 6 months), median',value=m,q1=q1,q3=q3,unit='days',
  source_url='https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf',
  source_table='Keuhkosyöpä Suomessa (Syöpärekisteri 2024), Taulukko 4.1, printed p.27 (PDF p.28); manually transcribed from table image') for a,h,m,q1,q3 in T]
with open(f'{D}/csv/lung_report2024_days_dx_to_first_treatment_by_yta.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows))
