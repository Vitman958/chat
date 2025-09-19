import asyncio
import logging
from datetime import datetime

from aioconsole import ainput
from logger_setup import get_logger
from list_commands import commands


class ListClients:
    def __init__(self):
        self.users = {}
        self.writers = set()

    def add_user(self, writer, nick_name):
        self.writers.add(writer)
        self.users[writer] = nick_name
    
    def remove_user(self, writer):
        self.writers.remove(writer)
        del self.users[writer]

    def check_user(self, nick_name):
        if nick_name in self.users.values():
            return False
        else:
            return True

    def get_users(self):
        return self.writers
    
    def get_user(self, writer):
        if writer is None:
            return 
        return self.users[writer]
    

logger = get_logger(__name__)


async def broadcast(message, users, sender_name, exclude_writer=None):
    writers = users.get_users()
    time = datetime.now().strftime("%H:%M")
    print(f"Broadcasting to {len(writers)} users")
    for writer in writers:
        if writer is exclude_writer:
            continue
        writer.write(f"[{time}][{sender_name}]: {message}\n".encode())
        await writer.drain()
        

async def handle_read(reader, writer, nick_name, stop_event, users):
    try:
        while True:
            try:
                data = await reader.readline()
                
                if not data:
                    users.remove_user(writer)
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
                    users.remove_user(writer)
                    print(f"Пользователь [{nick_name}] вышел с сервера")
                    logger.info(f"Пользователь {nick_name} вышел с сервера")
                    break
                
                else:
                    time = datetime.now().strftime("%H:%M")
                    await broadcast(msg, users, nick_name, exclude_writer=writer)
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


async def handle_write(writer, server_name, stop_event, users):
    try:
        while True:
            try:
                if stop_event.is_set():
                    break
                msg = await ainput()
                await broadcast(msg, users, server_name)
                
            except Exception as e:
                logging.error(f"Сетевая ошибка при отправке от {server_name}: {e}")

    except Exception as e:
        logger.error(f"Ошибка запуска handle_write")


def create_handler(users, server_name):
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


async def main():
    server_name = await ainput("Имя сервера: ")
    logger.info(f"Создан сервер с именем: {server_name}")
    users = ListClients()

    handler = create_handler(users, server_name)

    server = await asyncio.start_server(
        handler, 'localhost', 8888
    )


    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())