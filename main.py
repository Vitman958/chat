import asyncio
import logging
from datetime import datetime

from aioconsole import ainput
from logger_setup import get_logger


logger = get_logger(__name__)


async def handle_read(reader, nick_name, stop_event):
    while True:
        data = await reader.readline()
        if not data:
            print(f"Пользователь [{nick_name}] вышел с сервера")
            logger.warning(f"Пользователь {nick_name} вышел с сервера")
            stop_event.set()
            break

        msg = data.decode().strip()
        if msg == "/exit":
            stop_event.set()
            print(f"Пользователь [{nick_name}] вышел с сервера")
            logger.info(f"Пользователь {nick_name} вышел с сервера")
            break
        print(msg)
        logger.info(f"Пользователь {nick_name} отправил сообщение")


async def handle_write(writer, server_name, stop_event):
    while True:
        if stop_event.is_set():
            break
        msg = await ainput()
        time = datetime.now().strftime("%H:%M")
        writer.write(f"[{time}][{server_name}]: {msg}\n".encode())
        await writer.drain()


async def main():
    server_name = await ainput("Имя сервера: ")
    logger.info(f"Создан сервер с именем: {server_name}")

    async def handle_client(reader, writer):
        name = await reader.readline()
        nick_name = name.decode().strip()
        print(f"Пользователь [{nick_name}] подключился на сервер")
        logger.info(f"Пользователь {nick_name} подключился к серверу")

        stop_event = asyncio.Event()
        read_task = asyncio.create_task(
            handle_read(reader, nick_name, stop_event)
        )
        write_task = asyncio.create_task(
            handle_write(writer, server_name, stop_event)
        )
        
        await stop_event.wait()
        await read_task
        await write_task
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(
        handle_client, 'localhost', 8888
    )

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())