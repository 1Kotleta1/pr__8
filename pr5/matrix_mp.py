"""Логика умножения матриц из практической работы №5 (pr5/1.py), вынесенная в модуль.

В исходной программе матрицы вводились с клавиатуры, а результат печатался в консоль.
Здесь та же функция multiply_part считает свою часть строк в отдельном процессе,
а multiply_parallel делит строки между процессами точно так же, как в 1.py.
"""
import random


def multiply_part(start, end, A, B):
    """Считает строки результата с start по end (как в pr5/1.py)."""
    rows = []
    for i in range(start, end):
        row = []
        for j in range(len(B[0])):
            sum_value = 0
            for k in range(len(B)):
                sum_value += A[i][k] * B[k][j]
            row.append(sum_value)
        rows.append(row)
    return rows


def split_rows(rows1, proc_count):
    """Делит строки первой матрицы между процессами (последний забирает остаток)."""
    proc_count = max(1, min(proc_count, rows1))
    part = rows1 // proc_count
    parts = []
    for i in range(proc_count):
        start = i * part
        end = rows1 if i == proc_count - 1 else start + part
        parts.append((start, end))
    return parts


def random_matrix(rows, cols, low=0, high=9):
    return [[random.randint(low, high) for _ in range(cols)] for _ in range(rows)]
