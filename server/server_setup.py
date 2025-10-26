import asyncio

from utils.logger_setup import get_logger


logger = get_logger(__name__)


def create_handler(users, server_name, handle_read, handle_write, broadcast, room_manager):
    async def handle_client(reader, writer):
        name = await reader.readline()
        nick_name = name.decode().strip()

        default_room = room_manager.get_room("general")
    
        if users.check_user(nick_name):  
            users.add_user(writer, nick_name)
            default_room.add_users(writer, nick_name)
            room_manager.assign_user_to_room(writer, default_room)

        else:
            writer.write(f"Этот никней уже занят\n".encode())
            await writer.drain()
            writer.close()
            return
        
        connection_msg = f"Пользователь [{nick_name}] подключился к серверу"
        await default_room.send_message(connection_msg, server_name, exclude_writer = writer)
        print(f"Пользователь [{nick_name}] подключился на сервер")
        logger.info(f"Пользователь {nick_name} подключился к серверу")

        stop_event = asyncio.Event()
        
        user_room = room_manager.get_user_room(writer)

        read_task = asyncio.create_task(
            handle_read(reader, writer, nick_name, stop_event, users, user_room, room_manager)
        )
        write_task = asyncio.create_task(
            handle_write(writer, server_name, stop_event, users, user_room)
        )

        await stop_event.wait()
        await read_task
        await write_task
        writer.close()
        await writer.wait_closed()
    return handle_client