import asyncio

from aioconsole import ainput
from client.handlers import handle_read, handle_write

async def main():
    """Точка запуска клиента"""
    reader, writer = await asyncio.open_connection("localhost", 8888)
    stop_event = asyncio.Event()

    asyncio.create_task(handle_read(reader, stop_event))

    nick_name = await ainput("Введите свое имя: ")
    writer.write((nick_name + '\n').encode())
    await writer.drain()

    asyncio.create_task(handle_write(writer, stop_event))

    await stop_event.wait()


if __name__ == '__main__':
    asyncio.run(main())
