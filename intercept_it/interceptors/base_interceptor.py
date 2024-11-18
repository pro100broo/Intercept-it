import asyncio
from typing import Callable, Coroutine

from intercept_it.utils.models import DefaultHandler
from intercept_it.utils.enums import ExecutionModesEnum, HandlersExecutionModesEnum
from intercept_it.loggers.base_logger import BaseLogger, BaseAsyncLogger
from intercept_it.utils.checker import arguments_checker
from intercept_it.utils.exceptions import InterceptItRunTimeException


class BaseInterceptor:
    """
    Implements loggers and handlers logic for any interceptor.
    Checks interceptor's setup parameters before the initialization
    """
    def __init__(
            self,
            exceptions: list[type[BaseException]] | None = None,
            loggers: list[BaseLogger | BaseAsyncLogger] | None = None,
            raise_exception: bool = False,
            send_function_parameters_to_handlers: bool = False,
            run_until_success: bool = False,
            execution_mode: str = ExecutionModesEnum.SYNCHRONOUS.value,
            handlers_execution_mode: str = HandlersExecutionModesEnum.ORDERED.value,
            loggers_execution_mode: str = HandlersExecutionModesEnum.ORDERED.value
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
        arguments_checker.check_setup_parameters(
            loggers,
            exceptions,
            raise_exception,
            send_function_parameters_to_handlers,
            run_until_success,
            execution_mode,
            handlers_execution_mode,
            loggers_execution_mode
        )

        self._handlers: list[DefaultHandler] | list[None] = []
        self._loggers = loggers
        self._send_function_parameters_to_handlers = send_function_parameters_to_handlers
        self._handlers_execution_mode = handlers_execution_mode
        self._loggers_execution_mode = loggers_execution_mode

    def __call__(self, *args, **kwargs):
        raise InterceptItRunTimeException('Invalid interceptor using. Use interceptor methods to call it')

    def register_handler(
            self,
            attached_callable: Callable,
            *args,
            execution_order: int = 1,
            receive_parameters: bool = False,
            **kwargs
    ) -> None:
        """
        Adds some callable to the specified ``Config`` class

        :param attached_callable: Specified function
        :param args: Positional arguments of function
        :param execution_order: Handlers execution order
        :param receive_parameters: Allows to receive parameters from the wrapped function
        :param kwargs: Keyword arguments of function
        """
        self._handlers.append(
            DefaultHandler(
                callable=attached_callable,
                args=args,
                execution_order=execution_order,
                receive_parameters=receive_parameters,
                kwargs=kwargs
            )
        )
        # Sorts handlers by execution_order parameter
        self._handlers = sorted(self._handlers, key=lambda priority: priority)

    def _execute_sync_handlers(self, exception: BaseException, *intercepted_args, **intercepted_kwargs) -> None:
        self._process_sync_loggers(str(exception))
        self._process_sync_handlers(intercepted_args, intercepted_kwargs)

    async def _execute_async_handlers(self, exception: BaseException, *intercepted_args, **intercepted_kwargs) -> None:
        await self._process_async_loggers(str(exception))
        await self._process_async_handlers(intercepted_args, intercepted_kwargs)

    def _process_sync_loggers(self, message: str) -> None:
        if self._loggers:
            [logger.save_logs(message) for logger in self._loggers]

    async def _process_async_loggers(self, message: str) -> None:
        if self._loggers:
            if self._loggers_execution_mode == HandlersExecutionModesEnum.ORDERED.value:
                [await logger.save_logs(message) for logger in self._loggers]
            else:
                await asyncio.gather(*[logger.save_logs(message) for logger in self._loggers])

    def _process_sync_handlers(self, args, kwargs) -> None:
        if self._handlers:
            if self._send_function_parameters_to_handlers:
                [
                    handler.callable(*handler.args, *args, **handler.kwargs, **kwargs)
                    if handler.receive_parameters
                    else handler.callable(*handler.args, **handler.kwargs)
                    for handler in self._handlers
                 ]
            else:
                [
                    handler.callable(*handler.args, **handler.kwargs)
                    for handler in self._handlers
                ]

    async def _process_async_handlers(self, args, kwargs) -> None:
        if self._handlers:
            handlers = await self._generate_handlers(args, kwargs)
            await self._execute_handlers(handlers)

    async def _generate_handlers(self, args, kwargs) -> list[Coroutine]:
        if self._send_function_parameters_to_handlers:
            return [
                handler.callable(*handler.args, *args, **handler.kwargs, **kwargs)
                if handler.receive_parameters
                else handler.callable(*handler.args, **handler.kwargs)
                for handler in self._handlers
            ]
        else:
            return [
                handler.callable(*handler.args, **handler.kwargs)
                for handler in self._handlers
            ]

    async def _execute_handlers(self, handlers: list[Coroutine]) -> None:
        if self._handlers_execution_mode == HandlersExecutionModesEnum.ORDERED.value:
            [await handler for handler in handlers]
        else:
            await asyncio.gather(*handlers)
