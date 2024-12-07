from datetime import datetime

from intercept_it import NestedInterceptor, GlobalInterceptor, UnitInterceptor, LoopedInterceptor
from intercept_it.loggers import STDLogger

from intercept_it.utils import cooldown_handler


global_interceptor = GlobalInterceptor(
            exceptions=[ZeroDivisionError, ValueError],
            loggers=[
                STDLogger(default_formatter=lambda message: f"{message} intercepted in global logger {datetime.now()}"),
            ],
        )

global_interceptor.register_handler(
    cooldown_handler,
    5
)

unit_interceptor = UnitInterceptor(
            loggers=[
                STDLogger(default_formatter=lambda message: f"{message} intercepted in unit logger {datetime.now()}")
            ]
        )

unit_interceptor.register_handler(
    cooldown_handler,
    5
)

looped_interceptor = LoopedInterceptor(
            exceptions=[ModuleNotFoundError],
            loggers=[
                STDLogger(default_formatter=lambda message: f"{message} intercepted in looped logger {datetime.now()}")
            ],
            timeout=2
        )

interceptor = NestedInterceptor(
    {
        'Global': global_interceptor,
        8: looped_interceptor,
        IndexError: unit_interceptor,
    }
)
