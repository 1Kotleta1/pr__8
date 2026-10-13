from playwright.sync_api import sync_playwright
S = 'report/screens/'
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    pg = b.new_page(viewport={'width': 1400, 'height': 860})
    pg.goto('http://127.0.0.1:5051'); pg.wait_for_timeout(2000)
    pg.get_by_role('button', name='NEW').click(); pg.wait_for_timeout(1000)
    pg.get_by_role('button', name='START').click()
    pg.wait_for_timeout(20000)
    pg.get_by_role('tab', name='Current Ratio').click(); pg.wait_for_timeout(2000)
    pg.screenshot(path=S + '12_ratio.png', full_page=True)
    pg.get_by_role('tab', name='Logs').click(); pg.wait_for_timeout(1500)
    pg.screenshot(path=S + '15_logs.png')
    pg.get_by_role('button', name='STOP').click(); pg.wait_for_timeout(3000)
    b.close()
