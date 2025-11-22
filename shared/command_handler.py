class CommandHandler:
    def __init__(self):
        self.commands = {
            "/help": self._handle_help,
            "/exit": self._handle_exit,
            "/connect": self._handle_connect,
            "/leave": self._handle_leave,
            "/rooms": self._handle_rooms
        }

    async def execute_command(self, command_name, **kwargs):
        method = self.commands.get(command_name)
        if method:
            await method(**kwargs)
            return True
        return False

    async def _handle_help(self, **kwargs):
        writer = kwargs["writer"]
        nick_name = kwargs["nick_name"]
        commands = kwargs["commands"]
        logger = kwargs["logger"]
        
        for command in commands:
            writer.write(f"[Сервер]: {command}\n".encode())
            await writer.drain()
            logger.info(f"Пользователь [{nick_name} запросил справку]")

    async def _handle_exit(self, **kwargs):
        writer = kwargs["writer"]
        stop_event = kwargs["stop_event"]
        room_manager = kwargs["room_manager"]
        current_room = kwargs["current_room"]
        remove_user_from_system = kwargs["remove_user_from_system"]
        nick_name = kwargs["nick_name"]
        users = kwargs["users"]
        logger = kwargs["logger"]

        stop_event.set()
        current_room = remove_user_from_system(writer, room_manager, users)

        info = f"Пользователь [{nick_name}] вышел с сервера"
        await current_room.send_message(info, "Сервер", exclude_writer=writer)
        print(f"Пользователь [{nick_name}] вышел с сервера, используя команду /exit")
        logger.info(f"Пользователь {nick_name} вышел с сервера")

    async def _handle_connect(self, **kwargs):
        writer = kwargs["writer"]
        msg = kwargs["msg"]
        room_manager = kwargs["room_manager"]
        current_room = kwargs["current_room"]
        nick_name = kwargs["nick_name"]

        room_name = msg[9:]
        if room_manager.check_room(room_name):
            leave_msg = f"Пользователь [{nick_name}] покинул комнату"
            await current_room.send_message(leave_msg, "Сервер", exclude_writer=writer)

            current_room.remove_users(writer)
            room_manager.delete_user_from_rooms(writer)
                            
            new_room = room_manager.get_room(room_name)
            new_room.add_users(writer, nick_name)
            room_manager.assign_user_to_room(writer, new_room)

            current_room = new_room

            writer.write(f"✅ Вы присоединились к комнате [{room_name}]\n".encode())
            await writer.drain()

            connect_msg = f"Пользователь [{nick_name}] присоединился к комнате"
            await current_room.send_message(connect_msg, "Сервер", exclude_writer=writer)

        else:
            writer.write("❌ Такой комнаты не существует\n".encode())
            await writer.drain()

    async def _handle_leave(self, **kwargs):
        writer = kwargs["writer"]
        room_manager = kwargs["room_manager"]
        current_room = kwargs["current_room"]
        nick_name = kwargs["nick_name"]

        if current_room.room == "general":
            writer.write("❌ Вы уже находитесь в главной комнате\n".encode())
            await writer.drain()
            return False

        leave_msg = f"Пользователь [{nick_name}] покинул комнату"
        await current_room.send_message(leave_msg, "Сервер", exclude_writer=writer)

        current_room.remove_users(writer)
        room_manager.delete_user_from_rooms(writer)

        default_room = room_manager.get_room("general")
        default_room.add_users(writer, nick_name)
        room_manager.assign_user_to_room(writer, default_room)

        enter_msg = f"Пользователь [{nick_name}] вошел в главную комнату"
        await default_room.send_message(enter_msg, "Сервер", exclude_writer=writer)

        writer.write("✅ Вы вернулись в главную комнату\n".encode())
        await writer.drain()

        return True
    
    async def _handle_rooms(self, **kwargs):
        writer = kwargs["writer"]
        room_manager = kwargs["room_manager"]

        all_rooms = room_manager.get_rooms()
        room_names = list(all_rooms.keys())
        rooms_list = "\n  • ".join(room_names)
        response = f"Доступные комнаты:\n  • {rooms_list}\n"
        writer.write(response.encode())
        await writer.drain()        
