import random
import multiprocessing


def multiply_part(start, end, A, B, result_list):
    for i in range(start, end):
        row = []
        for j in range(len(B[0])):
            sum_value = 0
            for k in range(len(B)):
                sum_value += A[i][k] * B[k][j]
            row.append(sum_value)
        result_list[i] = row


if __name__ == '__main__':
    print("Программа для умножения двух матриц с помощью процессов\n")


    rows1 = int(input("Введите количество строк первой матрицы: "))
    cols1 = int(input("Введите количество столбцов первой матрицы: "))
    rows2 = int(input("Введите количество строк второй матрицы: "))
    cols2 = int(input("Введите количество столбцов второй матрицы: "))

    if cols1 != rows2:
        print("Ошибка: количество столбцов первой матрицы должно быть равно количеству строк второй!")
        exit()
    max_proc = multiprocessing.cpu_count()
    proc_count = int(input(f"Введите количество процессов (максимум {max_proc}): "))
    if proc_count > max_proc:
        proc_count = max_proc


    A = []
    for i in range(rows1):
        row = []
        for j in range(cols1):
            row.append(random.randint(0, 9))
        A.append(row)

    B = []
    for i in range(rows2):
        row = []
        for j in range(cols2):
            row.append(random.randint(0, 9))
        B.append(row)

    print("\nМатрица A:")
    for row in A:
        print(row)

    print("\nМатрица B:")
    for row in B:
        print(row)

    result = multiprocessing.Manager().list([[0]*cols2 for _ in range(rows1)])


    part = rows1 // proc_count
    processes = []

    for i in range(proc_count):
        start = i * part
        if i == proc_count - 1:
            end = rows1
        else:
            end = start + part
        p = multiprocessing.Process(target=multiply_part, args=(start, end, A, B, result))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("\nРезультат умножения (матрица C):")
    for row in result:
        print(row)
