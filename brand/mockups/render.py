# Overview + Live via Playwright. How we built it: python3 howwebuilt.py --render (Chrome).
import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080})
    for name,out in [('overview','mockup-overview.png'),('live','mockup-live.png')]:
        if len(sys.argv)>1 and name not in sys.argv[1:]: continue
        pg.goto(f'file:///workspace/junction-new/brand/mockups/{name}.html'); pg.wait_for_timeout(1200)
        pg.screenshot(path=f'/workspace/junction-new/brand/{out}')
    b.close()
