import asyncio
from datetime import datetime

from aioconsole import ainput
from utils.list_commands import commands
from utils.logger_setup import get_logger
from shared.broadcast import broadcast


logger = get_logger(__name__)


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
                    info = f"Пользователь [{nick_name}] вышел с сервера"
                    await broadcast(info, users, "Сервер", exclude_writer=writer)
                    print(f"Пользователь [{nick_name}] вышел с сервера")
                    logger.info(f"Пользователь {nick_name} вышел с сервера")
                    break
                
                else:
                    time = datetime.now().strftime("%H:%M")
                    await broadcast(msg, users, nick_name, exclude_writer=writer)
                    print(f"[{time}][{nick_name}]: {msg}")
                    logger.info(f"Пользователь {nick_name} отправил сообщение")

            except (ConnectionResetError, asyncio.IncompleteReadError) as e:
                logger.error(f"Сетевая ошибка при чтении от {nick_name}: {e}")
                break
            
            except Exception as e:
                logger.error(f"Неожиданная ошибка при чтении от {nick_name}: {e}")
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
                logger.error(f"Сетевая ошибка при отправке от {server_name}: {e}")

    except Exception as e:
        logger.error(f"Ошибка запуска handle_write")