"""Графики по CSV-результатам Locust (results/main_run)."""
import csv
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

R = 'results/main_run/'
S = 'report/screens/'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11})

rows = [r for r in csv.DictReader(open(R + 'locust_stats_history.csv', encoding='utf-8'))
        if r['Name'] == 'Aggregated' and r['User Count'] != '0']
t = [datetime.fromtimestamp(int(r['Timestamp'])) for r in rows]
rps = [float(r['Requests/s']) for r in rows]
users = [int(r['User Count']) for r in rows]
p50 = [float(r['50%']) if r['50%'] != 'N/A' else 0 for r in rows]
p95 = [float(r['95%']) if r['95%'] != 'N/A' else 0 for r in rows]
fails = [float(r['Failures/s']) for r in rows]

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(t, rps, color='#1f9d55', label='Запросов в секунду (RPS)')
ax.plot(t, fails, color='#d9534f', label='Ошибок в секунду')
ax.set_ylabel('RPS')
ax2 = ax.twinx()
ax2.plot(t, users, color='#2b6cb0', linestyle='--', label='Пользователей')
ax2.set_ylabel('Пользователей')
ax2.set_ylim(0, 60)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc='lower right')
ax.set_title('Интенсивность запросов и число пользователей')
ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(S + '17_chart_rps.png', dpi=130)

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(t, p50, color='#f0a202', label='Медиана (50%)')
ax.plot(t, p95, color='#7b4fc9', label='95-й перцентиль')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
ax.set_ylabel('мс'); ax.set_title('Время ответа сервера'); ax.grid(alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig(S + '18_chart_latency.png', dpi=130)

stats = [r for r in csv.DictReader(open(R + 'locust_stats.csv', encoding='utf-8')) if r['Type']]
by_method = {}
for r in stats:
    by_method[r['Type']] = by_method.get(r['Type'], 0) + int(r['Request Count'])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={'width_ratios': [1, 2]})
colors = {'GET': '#2b6cb0', 'POST': '#1f9d55', 'PUT': '#f0a202', 'DELETE': '#d9534f'}
m = list(by_method)
bars = a1.bar(m, [by_method[k] for k in m], color=[colors[k] for k in m])
a1.bar_label(bars)
a1.set_title(f"Запросов по методам\nGET / POST = {by_method['GET'] / by_method['POST']:.1f}")
names = [f"{r['Type']} {r['Name']}" for r in stats]
avg = [float(r['Average Response Time']) for r in stats]
b2 = a2.barh(names, avg, color=[colors[r['Type']] for r in stats])
a2.bar_label(b2, fmt='%.1f')
a2.invert_yaxis(); a2.set_xlabel('мс'); a2.set_title('Среднее время ответа по запросам')
fig.tight_layout(); fig.savefig(S + '19_chart_methods.png', dpi=130)
print(by_method)
