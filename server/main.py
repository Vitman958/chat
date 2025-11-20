import asyncio

from aioconsole import ainput
from server.handlers import handle_read, handle_server_commands
from server.server_setup import create_handler
from utils.logger_setup import get_logger
from shared.users import ListClients
from shared.rooms import RoomManager
from shared.limits import RateLimiter
from shared.command_handler import CommandHandler

   
logger = get_logger(__name__)


async def main():
    server_name = await ainput("Имя сервера: \n")
    
    room = RoomManager()
    room.create_room("general")

    while True:
        print("Настройка сервера")
        setup_cmd = await ainput("Команда (/create или start): ")
        if setup_cmd == "start":
            break
        elif setup_cmd.startswith("/create "):
            room_name = setup_cmd[8:]
            if room.check_room(room_name):
                print(f"комнта {room_name} уже создана")
            else:
                room.create_room(room_name)
                print(f"комната {room_name} создана")
    

    users = ListClients()
    rate_limiter = RateLimiter()
    command_handler = CommandHandler()

    logger.info(f"Создан сервер с именем: {server_name}")
    print(f"Сервер {server_name} успешно создан")

    handler = create_handler(users, server_name, handle_read, room, rate_limiter, command_handler)

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