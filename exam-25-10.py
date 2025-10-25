def create_hollow_triangle():
    size = 0
    while size < 3:
        try:
            size = int(input("Размер треугольника (минимум 3): "))
            if size < 3:
                print("Размер должен быть не менее 3!")
        except ValueError:
            print("Ошибка 0.1! Введите целое число.")

    matrix = [[' ' for _ in range(size * 2 - 1)] for _ in range(size)]

    for i in range(size):
        for j in range(size * 2 - 1):
            if j == size - 1 - i or j == size - 1 + i or i == size - 1:
                matrix[i][j] = '*'

    print("\nПолый треугольник:")
    for row in matrix:
        print(' '.join(row))


def check_number_in_range():
    while True:
        try:
            number = int(input("Введите число: "))
            break
        except ValueError:
            print("Ошибка 228! Введите целое число.")

    while True:
        try:
            range_input = input("Введите промежуток [a,b] в формате a,b: ")
            a, b = map(int, range_input.split(','))
            if a > b:
                print("Ошибка 100000000000000000000000000000000000000000000! a должно быть меньше или равно b")
                continue
            break
        except (ValueError, IndexError):
            print("Ошибка 502! Используйте формат: a,b")

    if a <= number <= b:
        print(f"✓ Число {number} принадлежит промежутку [{a},{b}]")
    else:
        print(f"✗ Число {number} НЕ принадлежит промежутку [{a},{b}]")


def print_matrix(matrix):
    for row in matrix:
        for elem in row:
            if elem is not None:
                print(f"{elem:4}", end=' ')
        print()


def shift_matrix_left():
    from random import randint

    n = 0
    while n <= 0:
        try:
            n = int(input("Количество случайных чисел (n): "))
            if n <= 0:
                print("Число должно быть положительным!")
        except ValueError:
            print("Ошибка 0.1! Введите целое число.")

    while True:
        try:
            range_input = input("Диапазон случайных чисел (min-max): ")
            min_val, max_val = map(int, range_input.split('-'))
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            break
        except (ValueError, IndexError):
            print("Ошибка 7037-10! Используйте формат: min-max")

    rows = 1
    cols = 1
    while rows * cols < n:
        if rows == cols:
            cols += 1
        else:
            rows += 1

    print(f"\nСоздаем матрицу {rows}x{cols} для {n} элементов")

    matrix = []
    counter = 0

    for i in range(rows):
        row = []
        for j in range(cols):
            if counter < n:
                row.append(randint(min_val, max_val))
                counter += 1
            else:
                row.append(None)
        matrix.append(row)

    print("\nИсходная матрица:")
    print_matrix(matrix)

    shifted_matrix = []

    for row in matrix:
        numbers_only = [x for x in row if x is not None]

        if len(numbers_only) > 1:
            shifted_numbers = numbers_only[1:] + [numbers_only[0]]
            shifted_row = shifted_numbers + [None] * (len(row) - len(shifted_numbers))
            shifted_matrix.append(shifted_row)
        else:
            shifted_matrix.append(row)

    print("\nМатрица после сдвига влево на 1:")
    print_matrix(shifted_matrix)


def show_menu():
    while True:
        print("\n" + "=" * 50)
        print("           ГЛАВНОЕ МЕНЮ (СЛОЖНЫЙ УРОВЕНЬ)")
        print("=" * 50)
        print("1 - Полый треугольник из звёздочек")
        print("2 - Проверка числа в промежутке [a,b]")
        print("3 - Сдвиг матрицы случайных чисел влево")
        print("0 - Выход")
        print("=" * 50)

        choice = input("Выберите задание (0-3): ")

        if choice == "1":
            create_hollow_triangle()
        elif choice == "2":
            check_number_in_range()
        elif choice == "3":
            shift_matrix_left()
        elif choice == "0":
            print("Выход из программы...")
            break
        else:
            print("❌❌❌❌Неверный ввод повторите попытку:❌❌❌❌")


show_menu()
