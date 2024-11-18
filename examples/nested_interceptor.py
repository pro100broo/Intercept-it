import math
from datetime import datetime

from intercept_it import NestedInterceptor, GlobalInterceptor, UnitInterceptor
from intercept_it.loggers import STDLogger

from intercept_it.utils import cooldown_handler

nested_interceptor = NestedInterceptor(
    {
        'Global': GlobalInterceptor(
            exceptions=[ZeroDivisionError, ValueError],
            loggers=[
                STDLogger(default_formatter=lambda message: f"{message} intercepted in global logger {datetime.now()}"),
            ],
        ),
        IndexError: UnitInterceptor(
            loggers=[
                STDLogger(default_formatter=lambda message: f"{message} intercepted in unit logger {datetime.now()}")
            ]
        ),
    }
)

nested_interceptor.interceptors['Global'].register_handler(
    cooldown_handler,
    5
)

nested_interceptor.interceptors[IndexError].register_handler(
    cooldown_handler,
    5
)


@nested_interceptor.intercept('Global')
def dangerous_calculation1(some_number: int) -> float:
    return some_number / 0


def dangerous_calculation2(some_number: int) -> float:
    return math.sqrt(some_number)


@nested_interceptor.intercept(IndexError)
def dangerous_list_access(index: int) -> int:
    numbers = [1, 2, 3]
    return numbers[index]


if __name__ == '__main__':
    # Intercept in decorators
    dangerous_calculation1(5)
    dangerous_list_access(100)

    # Intercept in wrapper
    nested_interceptor.wrap(dangerous_calculation2, 'Global', -1)
