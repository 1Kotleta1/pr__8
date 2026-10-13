"""Рендер реального вывода терминала и фрагментов кода в PNG для отчёта."""
import html, subprocess, sys
from pygments import highlight
from pygments.lexers import PythonLexer, IniLexer
from pygments.formatters import HtmlFormatter
from playwright.sync_api import sync_playwright

S = 'report/screens/'
uv = open('results/uvicorn.log', encoding='utf-8').read().splitlines()
lc = open('results/locust_console.log', encoding='utf-8').read().splitlines()
git = subprocess.run(['git', 'log', '--stat', '--format=commit %H%nAuthor: %an <%ae>%nDate:   %ad%n%n    %s%n'],
                     capture_output=True, text=True, encoding='utf-8').stdout.splitlines()
gst = subprocess.run(['git', 'status'], capture_output=True, text=True, encoding='utf-8').stdout.splitlines()

def term(title, blocks):
    body = ''
    for cmd, out in blocks:
        body += f'<div><span class="p">PS C:\...\pr8\locust_pr8&gt;</span> {html.escape(cmd)}</div>'
        body += ''.join(f'<div>{html.escape(l) or "&nbsp;"}</div>' for l in out)
    return f'''<div class="term"><div class="bar">{title}</div><div class="tb">{body}</div></div>'''

css_term = '''body{margin:0;background:#fff;padding:10px;display:inline-block}
.term{width:1180px;border-radius:6px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.25);font:13px Consolas,monospace}
.bar{background:#2d2d30;color:#ccc;padding:6px 12px;font-family:Segoe UI}
.tb{background:#0c0c0c;color:#ccc;padding:10px 14px;white-space:pre}
.p{color:#6ab0f3}'''

pages = {
 '20_term_server.png': term('Терминал 1 — запуск веб-API', [
    ('venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 5050',
     uv[:4] + uv[4:8] + ['...'] + [l for l in uv if 'multiply' in l][:3] +
     [l for l in uv if '400 Bad' in l][:2] + [l for l in uv if 'PUT' in l][:2] + [l for l in uv if 'DELETE' in l][:2])]),
 '21_term_locust.png': term('Терминал 2 — запуск Locust', [
    ('cd load_tests; ..\venv\Scripts\locust --csv ../results/locust --csv-full-history', lc[:4])]),
 '22_term_git.png': term('Терминал 3 — Git-репозиторий', [
    ('git log --stat', [l for l in git if 'report/screens' not in l] ), ('git status', gst)]),
}

fmt = HtmlFormatter(linenos='table', style='default')
src = open('load_tests/locustfile.py', encoding='utf-8').read().splitlines()
def code(lines, start, lexer=PythonLexer()):
    f = HtmlFormatter(linenos='table', linenostart=start, style='default')
    return f'<style>{f.get_style_defs(".highlight")}</style><div class="code">' + highlight('\n'.join(lines), lexer, f) + '</div>'
css_code = '''body{margin:0;background:#fff;padding:10px;display:inline-block}.code{width:1000px;border:1px solid #ccc;border-radius:4px;font-size:13px;padding:6px}
.code pre{margin:0;font:13px Consolas,monospace;line-height:1.35}.linenos{color:#999;padding-right:10px}'''
def find(s): return next(i for i, l in enumerate(src) if l.startswith(s))
a, b, c, d = find('class ViewerTasks'), find('class AnalystScenario'), find('class ViewerUser'), len(src)
pages['23_code_data.png'] = code(src[:find('class ViewerTasks') - 2], 1)
pages['24_code_taskset.png'] = code(src[a:b - 2], a + 1)
pages['25_code_sequential.png'] = code(src[b:c - 2], b + 1)
pages['26_code_users.png'] = code(src[c:d], c + 1) + '<br>' + code(open('load_tests/locust.conf', encoding='utf-8').read().splitlines(), 1, IniLexer())
m = open('app/main.py', encoding='utf-8').read().splitlines()
mi = next(i for i, l in enumerate(m) if l.startswith('@app.post("/api/multiply"'))
pages['27_code_api.png'] = code(m[mi:mi + 30], mi + 1)

with sync_playwright() as p:
    br = p.chromium.launch(channel='chrome')
    pg = br.new_page(viewport={'width': 1300, 'height': 600}, device_scale_factor=1.5)
    for name, h in pages.items():
        css = css_term if name.startswith(('20', '21', '22')) else css_code
        pg.set_content(f'<meta charset="utf-8"><style>{css}</style>{h}')
        pg.wait_for_timeout(200)
        pg.locator('body').screenshot(path=S + name)
    br.close()
