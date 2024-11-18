from typing import Callable, Any

from intercept_it.interceptors.base_interceptor import BaseInterceptor
from intercept_it.loggers.base_logger import BaseLogger, BaseAsyncLogger
from intercept_it.utils.checker import arguments_checker
from intercept_it.utils.enums import ExecutionModesEnum


class GlobalInterceptor(BaseInterceptor):
    """ Intercepts specified exceptions from a function """

    def __init__(
            self,
            exceptions: list[type[BaseException]],
            loggers: list[BaseLogger | BaseAsyncLogger] | None = None,
            raise_exception: bool = False,
            send_function_parameters_to_handlers: bool = False,
            run_until_success: bool = False,
            execution_mode: str = "sync",
            handlers_execution_mode: str = "ordered",
            loggers_execution_mode: str = "ordered"
    ):
        """
        :param exceptions: Collection of target exceptions

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
            exceptions=exceptions,
            loggers=loggers,
            raise_exception=raise_exception,
            send_function_parameters_to_handlers=send_function_parameters_to_handlers,
            run_until_success=run_until_success,
            execution_mode=execution_mode,
            handlers_execution_mode=handlers_execution_mode,
            loggers_execution_mode=loggers_execution_mode
        )
        self._exceptions = exceptions
        self._raise_exception = raise_exception
        self._run_until_success = run_until_success
        self._execution_mode = execution_mode

    def intercept(self, function: Callable) -> Any:
        """
        Exceptions handler of the ``GlobalInterceptor`` object. Can be used as a decorator without parentheses

        Usage example::

        @global_interceptor.intercept
        def dangerous_function(number: int, accuracy=0.1) -> float:
        """
        if self._execution_mode == ExecutionModesEnum.ASYNCHRONOUS.value:
            async def wrapper(*args, **kwargs):
                return await self._async_wrapper(function, args, kwargs)
        else:
            def wrapper(*args, **kwargs):
                return self._sync_wrapper(function, args, kwargs)
        return wrapper

    def wrap(self, function: Callable, *args, **kwargs) -> Any:
        """
        Exceptions handler of the ``GlobalInterceptor`` object. Can be used as a function with parameters

        Usage example::

        global_interceptor.wrap(dangerous_function, 5, accuracy=0.3)

        :param function: Wrapped function
        :param args: Positional arguments of the function
        :param kwargs: Keyword arguments of the function
        """
        arguments_checker.check_function(function)
        if self._execution_mode == ExecutionModesEnum.ASYNCHRONOUS.value:
            async def wrapper():
                return await self._async_wrapper(function, args, kwargs)
            return wrapper()
        else:
            return self._sync_wrapper(function, args, kwargs)

    def _sync_wrapper(self, function: Callable, args, kwargs) -> Any:
        """
        Executes the main control logic of the wrapped function

        :param function: Wrapped function
        :param args: Positional arguments of the function
        :param kwargs: Keyword arguments of the function
        """
        while True:
            try:
                return function(*args, **kwargs)
            except BaseException as exception:
                if exception.__class__ not in self._exceptions:
                    raise exception

                self._execute_sync_handlers(exception, *args, **kwargs)

                if self._raise_exception:
                    raise exception

            if not self._run_until_success:
                break

    async def _async_wrapper(self, function: Callable, args, kwargs) -> Any:
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
                if exception.__class__ not in self._exceptions:
                    raise exception

                await self._execute_async_handlers(exception, *args, **kwargs)

                if self._raise_exception:
                    raise exception

            if not self._run_until_success:
                break
