import asyncio
from datetime import datetime

from aioconsole import ainput
from server.handlers import handle_read, handle_write
from server.server_setup import create_handler
from utils.logger_setup import get_logger
from utils.list_commands import commands
from shared.users import ListClients
<<<<<<< HEAD
from shared.broadcast import broadcast
=======
>>>>>>> 7be7c78f730908edbd9756273233088885e484a2

   
logger = get_logger(__name__)


async def main():
    server_name = await ainput("Имя сервера: ")
    users = ListClients()

    logger.info(f"Создан сервер с именем: {server_name}")

<<<<<<< HEAD
    handler = create_handler(users, server_name, handle_read, handle_write, broadcast)
=======
    handler = create_handler(users, server_name, handle_read, handle_write)
>>>>>>> 7be7c78f730908edbd9756273233088885e484a2

    server = await asyncio.start_server(
        handler, 'localhost', 8888
    )


    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())