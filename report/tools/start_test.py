"""Запускает тест в веб-интерфейсе Locust и останавливает его через N секунд."""
import sys
from playwright.sync_api import sync_playwright
secs = int(sys.argv[1]) if len(sys.argv) > 1 else 40
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    pg = b.new_page()
    pg.goto('http://127.0.0.1:5051'); pg.wait_for_timeout(2000)
    pg.get_by_role('button', name='START').click()
    pg.wait_for_timeout(secs * 1000)
    pg.get_by_role('button', name='STOP').click(); pg.wait_for_timeout(2000)
    b.close()
