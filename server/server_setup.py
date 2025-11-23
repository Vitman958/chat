import asyncio

from utils.list_commands import commands
from utils.logger_setup import get_logger
from utils.check_nickname import check_nickname


logger = get_logger(__name__)


def create_handler(users, server_name, handle_read, room_manager, rate_limiter, command_handler, database_manager):
    async def handle_client(reader, writer):
        try:
            name = await reader.readline()
            nick_name = name.decode().strip()

            allowed, error_msg = check_nickname(nick_name)
            if not allowed:
                writer.write(f"❌ {error_msg}\n".encode())
                await writer.drain()
                writer.close()
                return

            default_room = room_manager.get_room("general")

            if users.check_user(nick_name):  
                users.add_user(writer, nick_name)
                default_room.add_users(writer, nick_name)
                room_manager.assign_user_to_room(writer, default_room)

            else:
                writer.write(f"❌ Этот никней уже занят\n".encode())
                await writer.drain()
                writer.close()
                return

            connection_msg = f"Пользователь [{nick_name}] подключился к серверу"

            welcome_msg = f"Добро пожаловать на сервер {server_name}!\n\nДоступные команды:\n" + \
              "\n".join([f"  • {cmd}" for cmd in commands]) + "\n"

            writer.write(welcome_msg.encode())
            await writer.drain()

            messages = await database_manager.get_messages(room_name="general")
            for timestamp, sender, message in messages:
                formatted_msg = f"[{timestamp}][{sender}]: {message}\n"
                writer.write(formatted_msg.encode())
                await writer.drain()

            await default_room.send_message(connection_msg, server_name, exclude_writer = writer)
            print(f"Пользователь [{nick_name}] подключился на сервер")
            logger.info(f"Пользователь {nick_name} подключился к серверу")

            stop_event = asyncio.Event()

            read_task = asyncio.create_task(
                handle_read(reader, writer, nick_name, stop_event, users, room_manager, rate_limiter, command_handler, database_manager)
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