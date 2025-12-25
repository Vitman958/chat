import asyncio
import uuid

from utils.list_commands import commands
from utils.logger_setup import get_logger
from utils.check_nickname import check_nickname


logger = get_logger(__name__)


def create_handler(server_name, handle_read, room_manager, rate_limiter, command_handler, database_manager, auth_manager):
    async def handle_client(reader, writer):
        """Создание обработчиков подключений"""
        try:
            name = await reader.readline()
            nick_name = name.decode().strip()

            allowed, error_msg = check_nickname(nick_name)
            if not allowed:
                writer.write(f"❌ {error_msg}\n".encode())
                await writer.drain()
                writer.close()
                return

            default_room = await room_manager.get_room("general")

            if not await database_manager.check_user_exists(nick_name):
                user_id = str(uuid.uuid4())
                await room_manager.assign_user_to_room(writer, user_id, "general", nick_name)
            
            else:
                writer.write(f"❌ Этот никней уже занят\n".encode())
                await writer.drain()
                writer.close()
                return

            messages = await database_manager.get_messages(room_name="general")
            for timestamp, sender, message in messages:
                formatted_msg = f"[{timestamp}][{sender}]: {message}\n"
                writer.write(formatted_msg.encode())
                await writer.drain()

            connection_msg = f"Пользователь [{nick_name}] подключился к серверу"

            welcome_msg = f"Добро пожаловать на сервер {server_name}!\n\nДоступные команды:\n" + \
              "\n".join([f"  • {cmd}" for cmd in commands]) + "\n"

            writer.write(welcome_msg.encode())
            await writer.drain()            

            await default_room.send_message(connection_msg, server_name, exclude_writer = writer)
            print(f"Пользователь [{nick_name}] подключился на сервер")
            logger.info(f"Пользователь {nick_name} подключился к серверу")

            stop_event = asyncio.Event()

            read_task = asyncio.create_task(
                handle_read(reader, writer, nick_name, stop_event, user_id, room_manager, rate_limiter, command_handler, database_manager, auth_manager)
            )
        
            await stop_event.wait()
            await read_task
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    return handle_client