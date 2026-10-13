import sys, time, urllib.request
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
S = 'report/screens/'
L = 'http://127.0.0.1:5051'

def tab(pg, name, file, full=False, wait=1500):
    pg.get_by_role('tab', name=name).click()
    pg.wait_for_timeout(wait)
    pg.screenshot(path=S + file, full_page=full)

with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    pg = b.new_page(viewport={'width': 1400, 'height': 860})
    pg.goto(L)
    pg.wait_for_timeout(1500)
    pg.get_by_text('Advanced options').click()
    pg.wait_for_timeout(700)
    pg.screenshot(path=S + '04_locust_advanced.png')
    pg.get_by_role('button', name='START').click()
    pg.wait_for_timeout(30000)
    pg.screenshot(path=S + '05_running_30s.png')
    pg.wait_for_timeout(60000)
    tab(pg, 'Charts', '06_charts_running.png', full=True, wait=3000)
    tab(pg, 'Statistics', '07_stats_running.png')
    # ждём окончания run-time (3m)
    for _ in range(200):
        txt = pg.inner_text('body')
        if 'STOPPED' in txt: break
        pg.wait_for_timeout(2000)
    pg.wait_for_timeout(2000)
    tab(pg, 'Statistics', '08_stats_final.png', full=True)
    tab(pg, 'Charts', '09_charts_final.png', full=True, wait=3000)
    tab(pg, 'Failures', '10_failures.png')
    tab(pg, 'Exceptions', '11_exceptions.png')
    tab(pg, 'Current Ratio', '12_ratio.png', full=True)
    tab(pg, 'Download Data', '13_download.png')
    print([t.inner_text() for t in pg.get_by_role('tab').all()])
    for url, f in [('/stats/report?download=1&theme=light', 'results/locust_report.html'),
                   ('/stats/requests/csv', 'results/requests.csv'),
                   ('/stats/failures/csv', 'results/failures.csv')]:
        urllib.request.urlretrieve(L + url, f)
    rp = b.new_page(viewport={'width': 1400, 'height': 900})
    import pathlib
    rp.goto(pathlib.Path('results/locust_report.html').resolve().as_uri())
    rp.wait_for_timeout(4000)
    rp.screenshot(path=S + '14_report.png', full_page=True)
    b.close()
