import logging

from intercept_it import GlobalInterceptor
from intercept_it.loggers.base_logger import BaseLogger

from intercept_it.utils import cooldown_handler


# Custom logger
class CustomLogger(BaseLogger):
    def __init__(self):
        self._logger = logging.getLogger()

    def save_logs(self, message: str) -> None:
        self._logger.warning(f'Be careful! Im custom logger: {message}')


# Initialize interceptor's object with necessary configuration
interceptor = GlobalInterceptor(
    [IndexError, ZeroDivisionError],  # Collection of subscribed exceptions
    loggers=[CustomLogger()],
)

# Add some handlers to config
interceptor.register_handler(
    cooldown_handler,  # callable
    5,  # positional argument
    execution_order=1
)

interceptor.register_handler(
    lambda x, y: print(f'{x}. {y}'),  # another callable :)
    'I am additional handler', 'It is so cool!',  # a few positional arguments
    execution_order=2
)


# Intercept the exceptions!
@interceptor.intercept
def dangerous_calculation(some_number: int) -> float:
    return some_number / 0


# Intercept the exceptions!
@interceptor.intercept
def dangerous_list_access(index: int) -> int:
    numbers = [1, 2, 3]
    return numbers[index]


if __name__ == '__main__':
    dangerous_calculation(5)
    dangerous_list_access(100)
