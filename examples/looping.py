import random

from intercept_it import LoopedInterceptor
from intercept_it import STDLogger


class RequestsException(Exception):
    pass


# Initialize interceptor's object with necessary configuration
interceptor = LoopedInterceptor(
    exceptions=[RequestsException],
    loggers=[STDLogger(default_formatter=lambda error: f'Error occurred: {error}. Waiting for success connection')],
    timeout=5
)


# Simulating the webserver work
@interceptor.intercept
def receive_data_from_api(api_key: str) -> dict[str, str]:
    is_server_down = random.randint(0, 10)
    if is_server_down >= 4:
        raise RequestsException('Integration down to maintenance')

    print(f'Successful connection with api key: {api_key}')
    return {'user': 'pro100broo', 'password': '12345'}


if __name__ == '__main__':
    print(f'Received data from integration: {receive_data_from_api("_API_KEY_")}')
