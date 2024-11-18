import logging
from datetime import datetime
from pydantic import BaseModel

from intercept_it import UnitInterceptor
from intercept_it.loggers.base_logger import BaseAsyncLogger


# Custom exception
class RequestsException(Exception):
    pass


# Custom async logger
class CustomLogger(BaseAsyncLogger):
    def __init__(self):
        self._logger = logging.getLogger()

    async def save_logs(self, message: str) -> None:
        self._logger.error(f"{message} | {datetime.now()}")


# Custom message model
class MessageModel(BaseModel):
    message: str
    status: str

    def __str__(self) -> str:
        return f"Text: {self.message}. Status: {self.status}"


# Initialize interceptor's object with necessary configuration
interceptor = UnitInterceptor(
    loggers=[CustomLogger()],
    send_function_parameters_to_handlers=True,  # Enable sending parameters to handlers
    execution_mode='async'
)
