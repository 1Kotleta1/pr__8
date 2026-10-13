import sys
from playwright.sync_api import sync_playwright
S = 'report/screens/'
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    pg = b.new_page(viewport={'width': 1400, 'height': 860})
    pg.goto('http://127.0.0.1:5051')
    pg.wait_for_timeout(3000)
    pg.screenshot(path=S + 'tmp_reload.png')
    pg.get_by_role('tab', name='Charts').click(); pg.wait_for_timeout(3000)
    pg.screenshot(path=S + 'tmp_charts.png', full_page=True)
    b.close()
