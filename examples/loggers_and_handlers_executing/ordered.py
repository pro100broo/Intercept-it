import asyncio
from datetime import datetime

from intercept_it import UnitInterceptor


async def first_logging_operation() -> None:
    await asyncio.sleep(5)
    print(f'First handler delivered logs: {datetime.now()}')


async def second_logging_operation() -> None:
    await asyncio.sleep(5)
    print(f'Second handler delivered logs: {datetime.now()}')


# Initialize interceptor's object with necessary configuration
interceptor = UnitInterceptor(execution_mode='async')

interceptor.register_handler(
    first_logging_operation,
    execution_order=1
)

interceptor.register_handler(
    second_logging_operation,
    execution_order=2
)


@interceptor.intercept(ZeroDivisionError)
def dangerous_calculation(number: int):
    return number / 0


if __name__ == '__main__':
    asyncio.run(dangerous_calculation(100))
