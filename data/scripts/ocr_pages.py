"""OCR rendered PDF pages with RapidOCR (pip rapidocr_onnxruntime) -> text lines grouped by row (y). Used ONLY to cross-check manual transcriptions."""
import sys, json
from rapidocr_onnxruntime import RapidOCR
eng=RapidOCR()
for f in sys.argv[1:]:
    res,_=eng(f)
    items=sorted([( (b[0][1]+b[2][1])/2, b[0][0], t) for b,t,c in res])
    rows=[];cur=[];y0=None
    for y,x,t in items:
        if y0 is None or abs(y-y0)<12: cur.append((x,t)); y0=y if y0 is None else y0
        else: rows.append(cur); cur=[(x,t)]; y0=y
    rows.append(cur)
    out=f.rsplit('.',1)[0]+'.ocr.txt'
    with open(out,'w') as fh:
        for r in rows: fh.write(' | '.join(t for x,t in sorted(r))+'\n')
    print(out)
