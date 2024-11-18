import random

from intercept_it import UnitInterceptor
from intercept_it import STDLogger

from intercept_it.utils import cooldown_handler


class RequestsException(Exception):
    pass


# Initialize interceptor's object with necessary configuration
interceptor = UnitInterceptor(
    loggers=[STDLogger(default_formatter=lambda error: f'Error occurred: {error}. Waiting for success connection')],
    run_until_success=True
)

interceptor.register_handler(
    cooldown_handler,
    5,
    execution_order=2
)


# Simulating the webserver work
@interceptor.intercept(RequestsException)
def receive_data_from_api(api_key: str) -> dict[str, str]:
    is_server_down = random.randint(0, 10)
    if is_server_down >= 4:
        raise RequestsException('Integration down to maintenance')

    print(f'Successful connection with api key: {api_key}')
    return {'user': 'pro100broo', 'password': '12345'}


if __name__ == '__main__':
    print(f'Received data from integration: {receive_data_from_api("_API_KEY_")}')
