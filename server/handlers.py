import asyncio
from datetime import datetime

from aioconsole import ainput
from utils.list_commands import commands
from utils.logger_setup import get_logger


logger = get_logger(__name__)
NO_AUTH_COMMANDS = {"/login", "/register", "/help"}


async def remove_user_from_system(room_manager, user_id):
    """Удаления пользователя из системы."""
    current_room = await room_manager.get_user_room(user_id)

    await room_manager.delete_user_from_rooms(user_id)

    return current_room


async def handle_read(reader, writer, nick_name, stop_event, user_id, room_manager, rate_limiter, command_handler, database_manager, auth_manager):
    """Ручка для чтения и ответа на сообщения."""
    try:
        while True:
            try:
                room_name = await room_manager.get_user_room(user_id)
                current_room = await room_manager.get_room(room_name) if room_name else None
                
                data = await reader.readline()
                msg = data.decode().strip()

                if msg.startswith("/"):
                    if not auth_manager.is_authenticated(writer) and msg.split()[0] not in NO_AUTH_COMMANDS:
                        writer.write("❌ Введите /login [username] [password] для входа\n❌ Введите /register [username] [password] для аутентификации\n".encode())
                        await writer.drain()
                        continue
                    
                    command_name = msg.split()[0]
                    if command_name in command_handler.commands:
                        await handle_command(writer, msg, command_handler, user_id, stop_event, room_manager, current_room, nick_name, database_manager, auth_manager)
                        updated_room_name = await room_manager.get_user_room(user_id)
                        current_room = await room_manager.get_room(updated_room_name) if updated_room_name else None     
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
                    room_name_obj = current_room.room
                    if auth_manager.is_authenticated(writer) and not msg.startswith("/"):
                        await database_manager.save_message(
                            room_name=room_name_obj,
                            sender=nick_name,
                            message=msg,
                            timestamp=datetime.now().strftime("%H:%M")
                        )

                if auth_manager.is_authenticated(writer):
                    await current_room.send_message(msg, nick_name, exclude_writer=writer)
                    logger.info(f"Пользователь {nick_name} отправил сообщение")
                else:
                    writer.write("❌ Введите /login [username] [password] для входа\n❌ Введите /register [username] [password] для аутентификации\n".encode())

            except (ConnectionResetError, asyncio.IncompleteReadError) as e:
                current_room_name = await room_manager.get_user_room(user_id)
                current_room_obj = await room_manager.get_room(current_room_name) if current_room_name else None

                await remove_user_from_system(room_manager, user_id)
                    
                print(f"Пользователь [{nick_name}] вышел с сервера")
                logger.warning(f"Пользователь {nick_name} вышел с сервера, закрыв терминал")

                if current_room_obj:
                    exit_msg = f"Пользователь [{nick_name}] вышел с сервера"
                    await current_room_obj.send_message(exit_msg, "Сервер", exclude_writer=writer)
                
                stop_event.set()
                break
            
            except Exception as e:
                logger.error(f"Неожиданная ошибка при чтении от {nick_name}: {e}")
                break

    except Exception as e:
        logger.error(f"Ошибка запуска handle_read")


async def handle_server_commands(room_manager):
    """Обработка команд сервера."""
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


async def handle_command(writer, msg, command_handler, user_id, stop_event, room_manager, current_room, nick_name, database_manager, auth_manager):
    """Ручка для обработки команд пользователя"""
    command_name = msg.split()[0]

    await command_handler.execute_command(
        command_name=command_name,
        writer=writer,
        msg=msg,
        user_id=user_id,
        stop_event=stop_event,
        room_manager=room_manager,
        current_room=current_room,
        nick_name=nick_name,
        database_manager=database_manager,
        auth_manager=auth_manager,
        remove_user_from_system=remove_user_from_system,
        commands=commands,
        logger=logger
    )