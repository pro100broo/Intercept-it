import math
from interceptor_setup import interceptor


@interceptor.intercept('Global')
def dangerous_calculation1(some_number: int) -> float:
    return some_number / 0


@interceptor.intercept(IndexError)
def dangerous_list_access(index: int) -> int:
    numbers = [1, 2, 3]
    return numbers[index]


@interceptor.intercept(8)
def dangerous_import() -> None:
    import python


def dangerous_calculation2(some_number: int) -> float:
    return math.sqrt(some_number)


if __name__ == '__main__':
    dangerous_calculation1(5)
    dangerous_list_access(100)

    interceptor.wrap(dangerous_calculation2, 'Global', -1)

    dangerous_import()

