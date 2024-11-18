from typing import Callable, Any

from intercept_it.interceptors.base_interceptor import BaseInterceptor
from intercept_it.loggers.base_logger import BaseLogger, BaseAsyncLogger
from intercept_it.utils.checker import arguments_checker
from intercept_it.utils.enums import ExecutionModesEnum


class UnitInterceptor(BaseInterceptor):
    """ Intercepts specified exception from a function """
    def __init__(
            self,
            loggers: list[BaseLogger | BaseAsyncLogger] | None = None,
            raise_exception: bool = False,
            run_until_success: bool = False,
            send_function_parameters_to_handlers: bool = False,
            execution_mode: str = "sync",
            handlers_execution_mode: str = "ordered",
            loggers_execution_mode: str = "ordered"
    ):
        """
        :param loggers: Collection of loggers

        :param raise_exception: If equals ``True`` interceptor sends all caught exceptions higher up the call stack.
            If not specified, feature disabled

        :param run_until_success: If equals ``True`` interceptor executes the wrapped function with handlers and loggers
            until an exception occurs in endless cycle. If not specified, feature disabled.
            Note that if ``raise_exception`` parameter equals ``True`` the feature also won't work

        :param send_function_parameters_to_handlers: If equals ``True`` interceptor sends wrapped function parameters
            to some handlers. If not specified, feature disabled

        :param execution_mode: If equals ``async`` interceptor can wrap coroutines.
            If not specified, can wrap only ordinary functions.
            No interceptor can wrap two specified types of functions at the same time!

        :param handlers_execution_mode: If equals ``ordered`` handlers will be executed in order with await
            instruction. If equals ``fast`` they will be executed in asyncio.gather()

        :param loggers_execution_mode: If equals ``ordered`` loggers will be executed in order with await
            instruction. If equals ``fast`` they will be executed in asyncio.gather()
        """
        super().__init__(
            loggers=loggers,
            raise_exception=raise_exception,
            send_function_parameters_to_handlers=send_function_parameters_to_handlers,
            run_until_success=run_until_success,
            execution_mode=execution_mode,
            handlers_execution_mode=handlers_execution_mode,
            loggers_execution_mode=loggers_execution_mode
        )
        self._raise_exception = raise_exception
        self._run_until_success = run_until_success
        self._execution_mode = execution_mode

    def intercept(self, exception: type[BaseException]) -> Any:
        """
        Exceptions handler of the ``UnitInterceptor`` object. Can be used with specified ``Exception``

        Usage example::

        @unit_interceptor.intercept(ValueError)
        def dangerous_function(number: int, accuracy=0.1) -> float:

        :param exception: Target exception
        """
        def outer(function):
            arguments_checker.check_exceptions([exception])
            if self._execution_mode == ExecutionModesEnum.ASYNCHRONOUS.value:
                async def wrapper(*args, **kwargs):
                    return await self._async_wrapper(function, exception, args, kwargs)
            else:
                def wrapper(*args, **kwargs):
                    return self._sync_wrapper(function, exception, args, kwargs)
            return wrapper
        return outer

    def wrap(self, function: Callable, exception: type[BaseException], *args, **kwargs) -> Any:
        """
        Exceptions handler of the ``GlobalInterceptor`` object. Can be used as a function with parameters

        Usage example::

        unit_interceptor.wrap(dangerous_function, ValueError, 5, accuracy=0.3)

        :param function: Wrapped function
        :param exception: Target exception
        :param args: Positional arguments of the function
        :param kwargs: Keyword arguments of the function
        """
        arguments_checker.check_function(function)
        arguments_checker.check_exceptions([exception])
        if self._execution_mode == ExecutionModesEnum.ASYNCHRONOUS.value:
            async def wrapper():
                return await self._async_wrapper(function, exception, args, kwargs)
            return wrapper()
        else:
            return self._sync_wrapper(function, exception, args, kwargs)

    def _sync_wrapper(self, function: Callable, target_exception: type[BaseException], args, kwargs) -> Any:
        """
        Executes the main control logic of the wrapped function

        :param function: Wrapped function
        :param target_exception: Target exception
        :param args: Positional arguments of the function
        :param kwargs: Keyword arguments of the function
        """
        while True:
            try:
                return function(*args, **kwargs)
            except BaseException as exception:
                if exception.__class__ != target_exception:
                    raise exception

                self._execute_sync_handlers(exception, *args, **kwargs)

                if self._raise_exception:
                    raise exception

            if not self._run_until_success:
                break

    async def _async_wrapper(self, function: Callable, target_exception: type[BaseException], args, kwargs) -> Any:
        """
        Executes the main control logic of the wrapped coroutine

        :param function: Wrapped function
        :param args: Positional arguments of the function
        :param kwargs: Keyword arguments of the function
        """
        while True:
            try:
                return await function(*args, **kwargs)
            except BaseException as exception:
                if exception.__class__ != target_exception:
                    raise exception

                await self._execute_async_handlers(exception, *args, **kwargs)

                if self._raise_exception:
                    raise exception

            if not self._run_until_success:
                break
