import asyncio
from datetime import datetime

from aioconsole import ainput
from server.handlers import handle_read, handle_write
from server.server_setup import create_handler
from utils.logger_setup import get_logger
from utils.list_commands import commands
from shared.users import ListClients
from shared.broadcast import broadcast
from shared.rooms import RoomManager

   
logger = get_logger(__name__)


async def main():
    server_name = await ainput("Имя сервера: ")
    
    room = RoomManager()
    room_name = await ainput("Имя комнаты: ")

    general = room.create_room(room_name)

    users = ListClients()

    logger.info(f"Создан сервер с именем: {server_name}")

    handler = create_handler(server_name, handle_read, handle_write, broadcast, room)

    server = await asyncio.start_server(
        handler, 'localhost', 8888
    )


    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())