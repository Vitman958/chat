import asyncio
from datetime import datetime

from aioconsole import ainput


async def handle_read(reader, stop_event):
    while True:
        data = await reader.readline()
        if not data or stop_event.is_set():
            break
        print(data.decode().strip())


async def handle_write(writer, nick_name, stop_event):
    while True:
        msg = await ainput()
        if msg == "/exit":
            writer.write(f"{msg}\n".encode())
            print("Выход с сервера")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            stop_event.set()
            break

        time = datetime.now().strftime("%H:%M")
        writer.write(f"[{time}][{nick_name}]: {msg}\n".encode())
        await writer.drain()


async def main():
    reader, writer = await asyncio.open_connection("localhost", 8888)
    stop_event = asyncio.Event()

    asyncio.create_task(handle_read(reader, stop_event))

    nick_name = await ainput("Введите свое имя: ")
    writer.write((nick_name + '\n').encode())
    await writer.drain()

    asyncio.create_task(handle_write(writer, nick_name, stop_event))

    await stop_event.wait()


if __name__ == '__main__':
    asyncio.run(main())
