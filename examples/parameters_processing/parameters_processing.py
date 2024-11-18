import random
import asyncio

from entities import (
    MessageModel,
    RequestsException,
    interceptor
)


# Handler for not delivered messages
async def parameters_handler(message: MessageModel, send_requests_queue: asyncio.Queue) -> None:
    send_requests_queue.task_done()
    print(f'Intercepted message: {message}')
    message.status = 'Awaiting resend'
    await resend_requests_queue.put(message)


interceptor.register_handler(
    parameters_handler,
    receive_parameters=True  # Enable receiving parameters from wrapped function
)


# Attempt to send message
@interceptor.intercept(RequestsException)
async def send_message_to_server(message: MessageModel, tasks_queue: asyncio.Queue) -> None:
    is_server_down = random.randint(0, 10)
    if is_server_down == 10:
        raise RequestsException(f'Connection lost. Failed to send message: {message}')

    message.status = 'Delivered'
    tasks_queue.task_done()

    print(f'Message successfully delivered: {message}')


# Gets message from the queue and tries to send it
async def send_message(send_requests_queue: asyncio.Queue) -> None:
    while True:
        message_content = await send_requests_queue.get()
        await send_message_to_server(message_content, send_requests_queue)


# Simulating the appearance of messages
async def generate_messages(send_requests_queue: asyncio.Queue) -> None:
    [
        await send_requests_queue.put(
            MessageModel(
                message=random.choice(['Hi!', 'Hello!', "What's up!"]),
                status="Awaiting send"
            )
        ) for _ in range(20)
    ]


# The entrypoint
async def main():
    send_requests_queue = asyncio.Queue(maxsize=50)
    await generate_messages(send_requests_queue)

    tasks = [asyncio.create_task(send_message(send_requests_queue)) for _ in range(4)]

    await send_requests_queue.join()

    [task.cancel() for task in tasks]

    print(f'Message queue for sending: {send_requests_queue}')
    print(f'Message queue for resending: {resend_requests_queue}')


if __name__ == '__main__':
    resend_requests_queue = asyncio.Queue(maxsize=50)
    asyncio.run(main())
