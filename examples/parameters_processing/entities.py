import asyncio
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


# The stash of undelivered  messages
resend_requests_queue = asyncio.Queue(maxsize=50)


# Undelivered messages handler
async def parameters_handler(message: MessageModel, send_requests_queue: asyncio.Queue) -> None:
    send_requests_queue.task_done()
    print(f'Intercepted message: {message}')
    message.status = 'Awaiting resend'
    await resend_requests_queue.put(message)


# Initialize interceptor's object with necessary configuration
interceptor = UnitInterceptor(
    loggers=[CustomLogger()],
    greed_mode=True,  # Enable routing parameters from the wrapped function to handlers
    async_mode=True  # Enable async code support
)


interceptor.register_handler(
    parameters_handler,
    receive_parameters=True  # Enable receiving wrapped function parameters from interceptor
)
