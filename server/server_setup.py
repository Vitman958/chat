import asyncio

from utils.logger_setup import get_logger


logger = get_logger(__name__)


def create_handler(users, server_name, handle_read, handle_write, broadcast):
    async def handle_client(reader, writer):
        name = await reader.readline()
        nick_name = name.decode().strip()

        if users.check_user(nick_name):  
            users.add_user(writer, nick_name)
        else:
            writer.write(f"Этот никней уже занят\n".encode())
            await writer.drain()
            writer.close()
            return 

        connection_msg = f"Пользователь [{nick_name}] подключился к серверу"
        await broadcast(connection_msg, users, server_name, exclude_writer = writer)
        print(f"Пользователь [{nick_name}] подключился на сервер")
        logger.info(f"Пользователь {nick_name} подключился к серверу")

        stop_event = asyncio.Event()
        read_task = asyncio.create_task(
            handle_read(reader, writer, nick_name, stop_event, users)
        )
        write_task = asyncio.create_task(
            handle_write(writer, server_name, stop_event, users)
        )

        await stop_event.wait()
        await read_task
        await write_task
        writer.close()
        await writer.wait_closed()
    return handle_client