import asyncio
from datetime import datetime

from intercept_it import UnitInterceptor


async def first_logging_operation() -> None:
    print(f'First handler received logs: {datetime.now()}')
    await asyncio.sleep(5)
    print(f'First handler delivered logs: {datetime.now()}')


async def second_logging_operation() -> None:
    print(f'Second handler received logs: {datetime.now()}')
    await asyncio.sleep(5)
    print(f'Second handler delivered logs: {datetime.now()}')


# Initialize interceptor's object with necessary configuration
interceptor = UnitInterceptor(async_mode=True)

interceptor.register_handler(first_logging_operation)
interceptor.register_handler(second_logging_operation)


@interceptor.intercept(ZeroDivisionError)
async def dangerous_calculation(number: int) -> float:
    return number / 0


if __name__ == '__main__':
    asyncio.run(dangerous_calculation(100))
