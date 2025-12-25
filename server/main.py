import asyncio

from aioconsole import ainput
from server.handlers import handle_read, handle_server_commands
from server.server_setup import create_handler
from utils.logger_setup import get_logger
from shared.rooms import RoomManager
from shared.limits import RateLimiter
from shared.command_handler import CommandHandler
from shared.database import DatabaseManager
from shared.auth_manager import AuthManager

   
logger = get_logger(__name__)


async def main():
    """Модуль запуска сервера"""
    server_name = await ainput("Имя сервера: \n")
    database_manager = DatabaseManager()
    await database_manager.init_db()

    rate_limiter = RateLimiter()
    command_handler = CommandHandler()
    auth_manager = AuthManager(database_manager)
    
    room = RoomManager(database_manager)    

    while True:
        print("Настройка сервера")
        setup_cmd = await ainput("Команда (/create или start): ")
        if setup_cmd == "start":
            break
        elif setup_cmd.startswith("/create "):
            room_name = setup_cmd[8:]
            if await room.check_room(room_name):
                print(f"❌комнта {room_name} уже создана")
            else:
                await room.create_room(room_name)
                print(f"✅комната {room_name} создана")
    

    logger.info(f"Создан сервер с именем: {server_name}")
    print(f"Сервер {server_name} успешно создан")

    handler = create_handler(server_name, handle_read, room, rate_limiter, command_handler, database_manager, auth_manager)

    server_task = asyncio.create_task(
        handle_server_commands(room))

    server = await asyncio.start_server(
        handler, 'localhost', 8888
    )


    async with server:
        await asyncio.gather(
            server.serve_forever(), 
            server_task
            )
        

if __name__ == '__main__':
    asyncio.run(main())