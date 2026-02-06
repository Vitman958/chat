from aioconsole import ainput
import asyncio
from typing import Any


async def handle_read(reader: Any, stop_event: asyncio.Event) -> None:
    """
    Обрабатывает чтение сообщений от сервера

    Args:
        reader: Объект для чтения данных из соединения
        stop_event: Событие для остановки цикла чтения
    """
    while True:
        data = await reader.readline()
        if not data or stop_event.is_set():
            break
        print(data.decode().strip())


async def handle_write(writer: Any, stop_event: asyncio.Event) -> None:
    """
    Обрабатывает отправку сообщений серверу

    Args:
        writer: Объект для записи данных в соединение
        stop_event: Событие для остановки цикла записи
    """
    while True:
        try:
            msg = await ainput()
            if msg == "/exit":
                writer.write(f"{msg}\n".encode())
                print("Выход с сервера")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                stop_event.set()
                break

            writer.write(f"{msg}\n".encode())
            await writer.drain()

        except ConnectionResetError:
            print("❌ Разорвано соединение с сервером")
            stop_event.set()
            break