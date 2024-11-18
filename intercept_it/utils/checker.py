import inspect
from typing import Callable, Any

from intercept_it.utils.exceptions import InterceptItSetupException, InterceptItRunTimeException
from intercept_it.loggers.base_logger import BaseLogger
from intercept_it.utils.enums import ExecutionModesEnum, HandlersExecutionModesEnum


class ArgumentsChecker:
    """
    Implements additional checks of interceptor parameters. Can raise two exceptions:

    * InterceptItSetupException when interceptor receives invalid parameters during initialization
    * InterceptItRunTimeException when interceptor receives invalid parameters at runtime
    """
    def check_setup_parameters(
            self,
            loggers: list[BaseLogger] | None = None,
            exceptions: list[type[BaseException]] | None = None,
            raise_exception: bool = False,
            send_function_parameters_to_handlers: bool = False,
            run_until_success: bool = False,
            execution_mode: str = ExecutionModesEnum.SYNCHRONOUS.value,
            handlers_execution_mode: str = HandlersExecutionModesEnum.ORDERED.value,
            loggers_execution_mode: str = HandlersExecutionModesEnum.ORDERED.value
    ) -> None:
        self.check_execution_mode(execution_mode)
        self.check_handlers_execution_mode(handlers_execution_mode)
        self.check_handlers_execution_mode(loggers_execution_mode)

        self.check_exceptions(exceptions)
        self.check_loggers(loggers)

        self.check_boolean_arguments(
            {
                'raise_exception': raise_exception,
                'send_function_parameters_to_handlers': send_function_parameters_to_handlers,
                'run_until_success': run_until_success
            }
        )

    def check_nested_interceptors(
            self,
            interceptors: dict[int | str | type[BaseException], Any],
            allowed_interceptors: list[Any]
    ) -> None:
        """
        Checks if group_ids and interceptors have invalid format

        :param interceptors: Interceptors collection
        :param allowed_interceptors: Allowed interceptors objects
        """
        for key in interceptors:
            if (
                    not isinstance(key, int) and
                    not isinstance(key, str) and
                    self.check_exceptions([key])
            ):
                raise InterceptItSetupException(
                    'Wrong key type for nested interceptors. Expected int or str or type[BaseException]'
                )

        for interceptor in interceptors.values():
            if (
                    not isinstance(interceptor, allowed_interceptors[0]) and
                    not isinstance(interceptor, allowed_interceptors[1])
            ):
                raise InterceptItSetupException(
                    f'Received invalid interceptor object: {interceptor.__class__}.\n'
                    f'Expected GlobalInterceptor or UnitInterceptor'
                )

    @staticmethod
    def check_execution_mode(execution_mode: str) -> None:
        if execution_mode not in ExecutionModesEnum:
            raise InterceptItSetupException(
                f'Wrong execution mode: {execution_mode}. Expected "sync" or "async"'
            )

    @staticmethod
    def check_handlers_execution_mode(execution_mode: str) -> None:
        if execution_mode not in HandlersExecutionModesEnum:
            raise InterceptItSetupException(
                f'Wrong handlers execution mode: {execution_mode}. Expected "fast" or "random"'
            )

    @staticmethod
    def check_exceptions(exceptions: list[type[BaseException]] | None) -> None:
        if exceptions:
            for exception in exceptions:
                try:
                    if not isinstance(exception(), BaseException):
                        raise InterceptItSetupException(
                            f'Received wrong exception object: {exception.__class__}'
                        )
                except TypeError:
                    raise InterceptItSetupException(
                        f'Received wrong exception object: {exception.__class__}'
                    )

    @staticmethod
    def check_loggers(loggers: list[BaseLogger] | None) -> None:
        """ Checks if all of received loggers are subclasses of the ``BaseLogger`` """
        if loggers:
            for logger in loggers:
                if not isinstance(logger, BaseLogger):
                    raise InterceptItSetupException(
                        f'Wrong logger subclass: {logger.__class__.__name__}. It must implements BaseLogger class'
                    )

    @staticmethod
    def check_boolean_arguments(arguments: dict[str, bool]) -> None:
        for name, value in arguments.items():
            if not isinstance(value, bool):
                raise InterceptItSetupException(
                    f'Wrong type for "{name}" parameter. Expected boolean'
                )

    @staticmethod
    def check_function(function: Callable) -> None:
        if not function:
            raise InterceptItRunTimeException('Target function not specified')
        # TODO: Протестировать на методах класса
        if not inspect.isfunction(function):
            raise InterceptItRunTimeException(f'Received invalid function: {function}')

    @staticmethod
    def check_group_existence(
            group_id: int | str | type[BaseException],
            interceptors: dict[int | str | type[BaseException], Any]
    ) -> Any:
        if not (group := interceptors.get(group_id)):
            raise InterceptItRunTimeException(
                f'Received invalid group_id: {group_id}'
            )
        return group


arguments_checker = ArgumentsChecker()
