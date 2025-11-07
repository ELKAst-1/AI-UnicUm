#1
def print_numbers(n):
    if n > 0:
        print_numbers(n - 1)
        print(n)

n = int(input())
print_numbers(n)

#2
def print_range(A, B):
    if A < B:
        print(A)
        print_range(A + 1, B)
    elif A > B:
        print(A)
        print_range(A - 1, B)
    else:
        print(A)

A = int(input())
B = int(input())
print_range(A, B)

#3
def is_power_of_two(n):
    if n == 1:
        return "YES"
    elif n % 2 != 0 or n == 0:
        return "NO"
    else:
        return is_power_of_two(n // 2)

n = int(input())
print(is_power_of_two(n))
#4
def fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

n = int(input())
print(fibonacci(n))
