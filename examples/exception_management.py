from intercept_it import GlobalInterceptor, UnitInterceptor

# Setup global interceptor
global_interceptor = GlobalInterceptor(
    [IndexError, ZeroDivisionError],
    raise_exception=True
)

global_interceptor.register_handler(
    lambda message: print(message),
    'Got exception in main function',
)

# Setup unit interceptor
unit_interceptor = UnitInterceptor(
    raise_exception=True
)

unit_interceptor.register_handler(
    lambda message: print(message),
    'Got exception in third-party function',
)


@unit_interceptor.intercept(ZeroDivisionError)
def dangerous_calculation(some_number: int) -> float:
    return some_number / 0


@global_interceptor.intercept
def main():
    dangerous_calculation(100)


if __name__ == '__main__':
    try:
        main()
    except ZeroDivisionError:
        print('Got exception in entry point')
