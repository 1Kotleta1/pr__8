"""Веб-API «Умножение матриц с помощью процессов» на базе практической работы №5.

Запуск: uvicorn app.main:app --host 127.0.0.1 --port 5050
"""
import asyncio
import json
import multiprocessing
import os
import sqlite3
import time
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from pr5.matrix_mp import multiply_part, random_matrix, split_rows

DB_PATH = Path(os.getenv("DB_PATH", Path(__file__).parent / "matrix.db"))
MAX_PROC = multiprocessing.cpu_count()
MAX_SIZE = 50

pool: ProcessPoolExecutor | None = None


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                rows1 INTEGER, cols1 INTEGER, rows2 INTEGER, cols2 INTEGER,
                processes INTEGER,
                elapsed_ms REAL,
                result TEXT,
                created_at TEXT
            )"""
        )


@asynccontextmanager
async def lifespan(_):
    global pool
    init_db()
    pool = ProcessPoolExecutor(max_workers=MAX_PROC)
    yield
    pool.shutdown()


app = FastAPI(title="Matrix multiplication API (PR5)", lifespan=lifespan)


class GenerateIn(BaseModel):
    rows: int = Field(ge=1, le=MAX_SIZE)
    cols: int = Field(ge=1, le=MAX_SIZE)
    low: int = 0
    high: int = 9


class MultiplyIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    a: list[list[int]]
    b: list[list[int]]
    processes: int = Field(ge=1)


class RenameIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


def check_matrix(m, name):
    if not m or not m[0] or len(m) > MAX_SIZE or len(m[0]) > MAX_SIZE:
        raise HTTPException(400, f"Матрица {name}: размер от 1 до {MAX_SIZE}")
    if any(len(r) != len(m[0]) for r in m):
        raise HTTPException(400, f"Матрица {name}: строки разной длины")


def row_to_dict(r, full=False):
    d = {k: r[k] for k in r.keys() if k != "result"}
    if full:
        d["result"] = json.loads(r["result"])
    return d


@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).parent / "index.html").read_text(encoding="utf-8")


@app.get("/api/system")
def system():
    return {"cpu_count": MAX_PROC, "max_size": MAX_SIZE}


@app.post("/api/matrices/generate")
def generate(data: GenerateIn):
    if data.low > data.high:
        raise HTTPException(400, "low больше high")
    return {"matrix": random_matrix(data.rows, data.cols, data.low, data.high)}


@app.post("/api/multiply", status_code=201)
async def multiply(data: MultiplyIn):
    check_matrix(data.a, "A")
    check_matrix(data.b, "B")
    rows1, cols1, rows2, cols2 = len(data.a), len(data.a[0]), len(data.b), len(data.b[0])
    if cols1 != rows2:
        raise HTTPException(400, "Количество столбцов первой матрицы должно быть равно количеству строк второй!")
    proc_count = min(data.processes, MAX_PROC)

    started = time.perf_counter()
    loop = asyncio.get_running_loop()
    futures = [loop.run_in_executor(pool, multiply_part, s, e, data.a, data.b)
               for s, e in split_rows(rows1, proc_count)]
    result = [row for part in await asyncio.gather(*futures) for row in part]
    elapsed = round((time.perf_counter() - started) * 1000, 2)

    with db() as conn:
        cur = conn.execute(
            "INSERT INTO calculations (title, author, rows1, cols1, rows2, cols2, processes, elapsed_ms, result, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data.title, data.author, rows1, cols1, rows2, cols2, proc_count, elapsed, json.dumps(result),
             datetime.now().isoformat(timespec="seconds")),
        )
    return {"id": cur.lastrowid, "processes": proc_count, "elapsed_ms": elapsed, "result": result}


@app.get("/api/history")
def history(limit: int = 20):
    with db() as conn:
        rows = conn.execute("SELECT * FROM calculations ORDER BY id DESC LIMIT ?", (min(limit, 100),)).fetchall()
    return [row_to_dict(r) for r in rows]


@app.get("/api/history/{calc_id}")
def history_item(calc_id: int):
    with db() as conn:
        r = conn.execute("SELECT * FROM calculations WHERE id = ?", (calc_id,)).fetchone()
    if not r:
        raise HTTPException(404, "Расчёт не найден")
    return row_to_dict(r, full=True)


@app.put("/api/history/{calc_id}")
def rename(calc_id: int, data: RenameIn):
    with db() as conn:
        cur = conn.execute("UPDATE calculations SET title = ? WHERE id = ?", (data.title, calc_id))
    if cur.rowcount == 0:
        raise HTTPException(404, "Расчёт не найден")
    return {"id": calc_id, "title": data.title}


@app.delete("/api/history/{calc_id}", status_code=204)
def delete(calc_id: int):
    with db() as conn:
        cur = conn.execute("DELETE FROM calculations WHERE id = ?", (calc_id,))
    if cur.rowcount == 0:
        raise HTTPException(404, "Расчёт не найден")


@app.get("/api/stats")
def stats():
    with db() as conn:
        r = conn.execute(
            "SELECT COUNT(*) AS total, ROUND(AVG(elapsed_ms), 2) AS avg_ms, MAX(rows1 * cols2) AS max_cells,"
            " COUNT(DISTINCT author) AS authors FROM calculations"
        ).fetchone()
    return dict(r)
