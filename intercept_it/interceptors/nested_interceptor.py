from typing import Callable, Any

from intercept_it.utils.checker import arguments_checker
from intercept_it.interceptors.global_interceptor import GlobalInterceptor
from intercept_it.interceptors.unit_interceptor import UnitInterceptor


class NestedInterceptor:
    """
    Subscribes to specific exception with unique processing logic.
    """
    def __init__(
            self,
            interceptors: dict[int | str | type[BaseException], GlobalInterceptor | UnitInterceptor]
    ):
        arguments_checker.check_nested_interceptors(interceptors, [GlobalInterceptor, UnitInterceptor])
        self.interceptors = interceptors

    def intercept(self, group_id: int | str | type[BaseException]) -> Any:
        def outer(function):
            group = arguments_checker.check_group_existence(group_id, self.interceptors)
            if isinstance(group, GlobalInterceptor):
                return group.intercept(function)
            else:
                return group.intercept(group_id)(function)
        return outer

    def wrap(self, function: Callable, group_id: int | str | type[BaseException], *args, **kwargs) -> Any:
        group = arguments_checker.check_group_existence(group_id, self.interceptors)
        if isinstance(group, GlobalInterceptor):
            return group.wrap(function, *args, **kwargs)
        else:
            return group.wrap(function, group_id, *args, **kwargs)
