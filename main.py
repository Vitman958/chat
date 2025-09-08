import asyncio
import logging
from datetime import datetime

from aioconsole import ainput
from logger_setup import get_logger
from list_commands import commands


logger = get_logger(__name__)


async def handle_read(reader, writer, nick_name, stop_event):
    try:
        while True:
            try:
                data = await reader.readline()
                if not data:
                    print(f"Пользователь [{nick_name}] вышел с сервера")
                    logger.warning(f"Пользователь {nick_name} вышел с сервера")
                    stop_event.set()
                    break

                msg = data.decode().strip()

                if msg == "/help":
                    for command in commands:
                        writer.write(f"[Сервер]: {command}\n".encode())
                        await writer.drain()
                        logger.info(f"Пользователь [{nick_name} запросил справку]")

                elif msg == "/exit":
                    stop_event.set()
                    print(f"Пользователь [{nick_name}] вышел с сервера")
                    logger.info(f"Пользователь {nick_name} вышел с сервера")
                    break
                
                else:
                    time = datetime.now().strftime("%H:%M")
                    print(f"[{time}][{nick_name}]: {msg}")
                    logger.info(f"Пользователь {nick_name} отправил сообщение")

            except (ConnectionResetError, asyncio.IncompleteReadError) as e:
                logging.error(f"Сетевая ошибка при чтении от {nick_name}: {e}")
                break
            except Exception as e:
                logging.error(f"Неожиданная ошибка при чтении от {nick_name}: {e}")
                break

    except Exception as e:
        logger.error(f"Ошибка запуска handle_read")


async def handle_write(writer, server_name, stop_event):
    try:
        while True:
            try:
                if stop_event.is_set():
                    break
                msg = await ainput()
                time = datetime.now().strftime("%H:%M")
                writer.write(f"[{time}][{server_name}]: {msg}\n".encode())
                await writer.drain()
            except Exception as e:
                logging.error(f"Сетевая ошибка при отправке от {server_name}: {e}")

    except Exception as e:
        logger.error(f"Ошибка запуска handle_write")


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
            handle_read(reader, writer, nick_name, stop_event)
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