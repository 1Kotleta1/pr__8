"""Нагрузочное тестирование веб-API «Умножение матриц с помощью процессов» (ПР №5).

TaskSet           - задачи выбираются случайно с учётом веса (поведение обычного пользователя).
SequentialTaskSet - задачи выполняются строго по порядку (сценарий «аналитика» от создания до удаления).
"""
import random

from faker import Faker
from locust import HttpUser, SequentialTaskSet, TaskSet, between, task

fake = Faker("ru_RU")

TOPICS = ["Расчёт нагрузки", "Матрица переходов", "Тест производительности", "Лабораторная",
          "Таблица продаж", "Модель сети", "Проверка процессов", "Отчёт по складу"]


def random_matrix(rows, cols):
    return [[fake.random_int(0, 9) for _ in range(cols)] for _ in range(rows)]


def calculation_payload():
    """Адекватные данные: согласованные размеры (столбцы A = строки B), числа 0-9, как в ПР №5."""
    n, m, k = random.randint(2, 12), random.randint(2, 12), random.randint(2, 12)
    return {
        "title": f"{random.choice(TOPICS)} {fake.month_name()} №{fake.random_int(1, 99)}",
        "author": fake.name(),
        "a": random_matrix(n, m),
        "b": random_matrix(m, k),
        "processes": random.randint(1, 4),
    }


class ViewerTasks(TaskSet):
    """Пользователь просматривает приложение: сумма весов GET = 20, POST = 1 (GET в 20 раз чаще)."""

    def on_start(self):
        self.known_ids = []

    @task(4)
    def open_main_page(self):
        self.client.get("/")

    @task(4)
    def view_history(self):
        limit = random.choice([5, 10, 20])
        with self.client.get("/api/history", params={"limit": limit}, name="/api/history",
                             catch_response=True) as resp:
            if resp.status_code == 200 and isinstance(resp.json(), list):
                resp.success()
            else:
                resp.failure("история не получена")

    @task(5)
    def view_calculation(self):
        if not self.known_ids:
            return self.view_history()
        calc_id = random.choice(self.known_ids)
        self.client.get(f"/api/history/{calc_id}", name="/api/history/[id]")

    @task(4)
    def view_stats(self):
        self.client.get("/api/stats")

    @task(3)
    def system_info(self):
        self.client.get("/api/system")

    @task(1)
    def multiply(self):
        resp = self.client.post("/api/multiply", json=calculation_payload())
        if resp.status_code == 201:
            self.known_ids.append(resp.json()["id"])


class AnalystScenario(SequentialTaskSet):
    """Аналитик: полный жизненный цикл расчёта строго по шагам."""

    calc_id = None

    @task
    def check_system(self):
        self.cpu = self.client.get("/api/system").json()["cpu_count"]

    @task
    def generate_matrices(self):
        n, m, k = random.randint(5, 20), random.randint(5, 20), random.randint(5, 20)
        resp = self.client.post("/api/matrices/generate", json={"rows": n, "cols": m, "low": 0, "high": 9})
        self.a = resp.json()["matrix"]
        self.b = random_matrix(m, k)  # вторую матрицу генерирует Faker на стороне клиента

    @task
    def multiply(self):
        payload = {"title": f"{random.choice(TOPICS)} ({fake.city()})", "author": fake.name(),
                   "a": self.a, "b": self.b, "processes": random.randint(1, self.cpu)}
        self.calc_id = self.client.post("/api/multiply", json=payload).json()["id"]

    @task
    def view_result(self):
        self.client.get(f"/api/history/{self.calc_id}", name="/api/history/[id]")

    @task
    def wrong_sizes(self):
        """Негативная проверка: несогласованные размеры должны вернуть 400, как ошибка в ПР №5."""
        payload = calculation_payload()
        payload["b"] = random_matrix(len(payload["a"][0]) + 1, 3)
        with self.client.post("/api/multiply", json=payload, name="/api/multiply [400]",
                              catch_response=True) as resp:
            if resp.status_code == 400:
                resp.success()
            else:
                resp.failure(f"ожидался 400, получен {resp.status_code}")

    @task
    def rename(self):
        title = f"{fake.word().capitalize()} — проверено {fake.first_name()}"
        self.client.put(f"/api/history/{self.calc_id}", json={"title": title}, name="/api/history/[id]")

    @task
    def check_renamed(self):
        self.client.get(f"/api/history/{self.calc_id}", name="/api/history/[id]")

    @task
    def view_history(self):
        self.client.get("/api/history", params={"limit": 10}, name="/api/history")

    @task
    def view_stats(self):
        self.client.get("/api/stats")

    @task
    def delete(self):
        self.client.delete(f"/api/history/{self.calc_id}", name="/api/history/[id]")
        self.calc_id = None

    def on_stop(self):
        # если тест остановили посреди сценария, удаляем созданный расчёт
        if self.calc_id:
            self.client.delete(f"/api/history/{self.calc_id}", name="/api/history/[id]")


class ViewerUser(HttpUser):
    weight = 4
    tasks = [ViewerTasks]
    wait_time = between(1, 3)


class AnalystUser(HttpUser):
    weight = 1
    tasks = [AnalystScenario]
    wait_time = between(1, 3)
