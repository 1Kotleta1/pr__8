# Практическая работа №8 — нагрузочное тестирование с помощью Locust

Объект тестирования — практическая работа №5 «Умножение двух матриц с помощью процессов»
(`pr5/1.py`). Логика умножения вынесена в модуль `pr5/matrix_mp.py` и опубликована
как веб-API на FastAPI (`app/main.py`): строки матрицы A по-прежнему делятся между
процессами (`ProcessPoolExecutor`), результаты расчётов сохраняются в SQLite.

## Структура

```
pr5/1.py              исходная консольная программа (ПР №5)
pr5/matrix_mp.py      функции multiply_part / split_rows / random_matrix
app/main.py           веб-API (FastAPI)
app/index.html        веб-страница приложения
load_tests/           locustfile.py и locust.conf
results/main_run/     CSV и HTML-отчёт Locust основного прогона
report/screens/       скриншоты и графики для отчёта
```

## Эндпоинты

| Метод  | Путь                       | Назначение                                 |
|--------|----------------------------|--------------------------------------------|
| GET    | `/`                        | веб-страница                               |
| GET    | `/api/system`              | число ядер CPU (максимум процессов)        |
| POST   | `/api/matrices/generate`   | сгенерировать случайную матрицу            |
| POST   | `/api/multiply`            | умножить A×B процессами, сохранить расчёт  |
| GET    | `/api/history`             | история расчётов                           |
| GET    | `/api/history/{id}`        | расчёт с результатом                       |
| PUT    | `/api/history/{id}`        | переименовать расчёт                       |
| DELETE | `/api/history/{id}`        | удалить расчёт                             |
| GET    | `/api/stats`               | статистика                                 |

## Запуск

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 5050
cd load_tests
..\venv\Scripts\locust
```

Веб-интерфейс Locust: http://127.0.0.1:5051 (порт задан в `locust.conf`).

## Сценарии

* `ViewerUser` (вес 4) → `ViewerTasks(TaskSet)`: случайные задачи по весам,
  GET-запросы (сумма весов 20) в 20 раз чаще POST (вес 1).
* `AnalystUser` (вес 1) → `AnalystScenario(SequentialTaskSet)`: строгий порядок —
  system → generate → multiply → просмотр → негативная проверка (400) → rename →
  проверка → history → stats → delete.

Тестовые данные генерируются библиотекой Faker (`ru_RU`): названия, ФИО авторов,
города, размеры и элементы матриц.

Итог основного прогона (50 пользователей, 3 минуты): 4341 запрос, 0 ошибок,
GET : POST = 3706 : 461 ≈ 8 : 1.
