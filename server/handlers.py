import asyncio

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


async def handle_read(reader, writer, nick_name, stop_event, users, room_manager):
    try:
        while True:
            try:
                current_room = room_manager.get_user_room(writer)
                
                data = await reader.readline()
                msg = data.decode().strip()

                if msg == "/help":
                    for command in commands:
                        writer.write(f"[Сервер]: {command}\n".encode())
                        await writer.drain()
                        logger.info(f"Пользователь [{nick_name} запросил справку]")

                elif msg == "/exit":
                    stop_event.set()
                    current_room = remove_user_from_system(writer, room_manager, users)
                    
                    info = f"Пользователь [{nick_name}] вышел с сервера"
                    await current_room.send_message(info, "Сервер", exclude_writer=writer)
                    print(f"Пользователь [{nick_name}] вышел с сервера, используя команду /exit")
                    logger.info(f"Пользователь {nick_name} вышел с сервера")
                    break

                elif msg.startswith("/connect "):
                    room_name = msg[9:]
                    if room_manager.check_room(room_name):
                        current_room.remove_users(writer)

                        room_manager.delete_user_from_rooms(writer)
                            
                        new_room = room_manager.get_room(room_name)
                        new_room.add_users(writer, nick_name)
                        room_manager.assign_user_to_room(writer, new_room)

                        current_room = new_room
                    else:
                        writer.write("Такой комнаты не существует\n".encode())
                        await writer.drain()
                    
                elif msg == "/leave":
                    if current_room.room == "general":
                        writer.write(f"Вы уже находитесь в главной комнате\n".encode())
                        await writer.drain()
                        continue

                    leave_msg = f"Пользователь [{nick_name}] покинул комнату"
                    await current_room.send_message(leave_msg, "Сервер", exclude_writer=writer)

                    current_room.remove_users(writer)
                    room_manager.delete_user_from_rooms(writer)

                    default_room = room_manager.get_room("general")
                    default_room.add_users(writer, nick_name)
                    room_manager.assign_user_to_room(writer, default_room)

                    enter_msg = f"Пользователь [{nick_name}] вошел в главную комнату"
                    await default_room.send_message(enter_msg, "Сервер", exclude_writer=writer)

                    writer.write("Вы вернулись в главную комнату\n".encode())
                    await writer.drain()

                elif msg == "/rooms":
                    all_rooms = room_manager.get_rooms()
                    room_names = list(all_rooms.keys())
                    rooms_list = ", ".join(room_names)
                    writer.write(f"Список комнат: {rooms_list}\n".encode())
                    await writer.drain()

                else:
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