import asyncio
from datetime import datetime

from aioconsole import ainput
from utils.list_commands import commands
from utils.logger_setup import get_logger


logger = get_logger(__name__)


def remove_user_from_system(writer, room_manager, users):
    """Удаления пользователя из системы."""
    current_room = room_manager.get_user_room(writer)
       
    if current_room:
        current_room.remove_users(writer)
        room_manager.delete_user_from_rooms(writer)
    
    users.remove_user(writer)
    return current_room


async def handle_read(reader, writer, nick_name, stop_event, users, room_manager, rate_limiter, command_handler, database_manager):
    try:
        while True:
            try:
                current_room = room_manager.get_user_room(writer)
                
                data = await reader.readline()
                msg = data.decode().strip()

                if msg.startswith("/"):
                    response = await handle_command(writer, msg, command_handler, users, stop_event, room_manager, current_room, nick_name, database_manager)   
                    if response:
                        continue
                    else:
                        writer.write(f"❌Такой команды не существует!\n".encode())

                else:
                    allowed, error_msg = rate_limiter.can_send_message(writer, msg)
                    if not allowed:
                        writer.write(f"❌ {error_msg}\n".encode())
                        await writer.drain()
                        continue
                    rate_limiter.update_time(writer)                

                
                if current_room:
                    room_name = current_room.room
                    await database_manager.save_message(
                        room_name=room_name,
                        sender=nick_name,
                        message=msg,
                        timestamp=datetime.now().strftime("%H:%M")
                    )

                await current_room.send_message(msg, nick_name, exclude_writer=writer)
                logger.info(f"Пользователь {nick_name} отправил сообщение")

            except (ConnectionResetError, asyncio.IncompleteReadError) as e:
                current_room = remove_user_from_system(writer, room_manager, users)
                    
                print(f"Пользователь [{nick_name}] вышел с сервера")
                logger.warning(f"Пользователь {nick_name} вышел с сервера, закрыв терминал")

                if current_room:
                    exit_msg = f"Пользователь [{nick_name}] вышел с сервера"
                    await current_room.send_message(exit_msg, "Сервер", exclude_writer=writer)
                
                stop_event.set()
                break
            
            except Exception as e:
                logger.error(f"Неожиданная ошибка при чтении от {nick_name}: {e}")
                break

    except Exception as e:
        logger.error(f"Ошибка запуска handle_read")


async def handle_server_commands(room_manager):
    try:
        while True:                
            msg = await ainput()

            if msg.startswith("/create "):
                room_name = msg[8:]
                if room_manager.check_room(room_name):
                    print(f"комнта {room_name} уже создана")
                else:
                    room_manager.create_room(room_name)
                    print(f"комната {room_name} создана")

    except Exception as e:
        logger.error(f"Ошибка запуска handle_server_commands")


async def handle_command(writer, msg, command_handler, users, stop_event, room_manager, current_room, nick_name, database_manager):
    command_name = msg.split()[0]

    result = await command_handler.execute_command(
        command_name=command_name,
        writer=writer,
        msg=msg,
        users=users,
        stop_event=stop_event,
        room_manager=room_manager,
        current_room=current_room,
        nick_name=nick_name,
        database_manager=database_manager,
        remove_user_from_system=remove_user_from_system,
        commands=commands,
        logger=logger
    )
    return result