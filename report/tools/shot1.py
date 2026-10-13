import sys
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
S = 'report/screens/'
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    pg = b.new_page(viewport={'width': 1400, 'height': 820})
    # приложение: ручной расчёт через UI
    pg.goto('http://127.0.0.1:5050/')
    pg.fill('#title', 'Проверка перед нагрузкой')
    pg.fill('#author', 'Георгий')
    pg.fill('#r1', '6'); pg.fill('#c1', '4'); pg.fill('#r2', '4'); pg.fill('#c2', '5'); pg.fill('#proc', '3')
    pg.click('text=Сгенерировать и умножить')
    pg.wait_for_selector('#out pre')
    pg.wait_for_timeout(800)
    pg.screenshot(path=S + '01_app.png')
    pg.goto('http://127.0.0.1:5050/docs')
    pg.wait_for_timeout(2500)
    pg.screenshot(path=S + '02_swagger.png', full_page=True)
    pg.goto('http://127.0.0.1:5051/')
    pg.wait_for_timeout(2500)
    pg.screenshot(path=S + '03_locust_start.png')
    print([e.get_attribute('name') for e in pg.query_selector_all('input')])
    print([e.inner_text() for e in pg.query_selector_all('button')])
    b.close()
