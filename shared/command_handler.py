class CommandHandler:
    def __init__(self):
        """Инициализация списка команд"""
        self.commands = {
            "/help": self._handle_help,
            "/exit": self._handle_exit,
            "/connect": self._handle_connect,
            "/leave": self._handle_leave,
            "/rooms": self._handle_rooms,
            "/login": self._handle_login,
            "/register": self._handle_register,
            "/logout": self._handle_logout
        }

    async def execute_command(self, command_name, **kwargs):
        """Проверка на существование команды"""
        method = self.commands.get(command_name)
        if method:
            await method(**kwargs)
            return True
        return False

    async def _handle_help(self, **kwargs):
        """Команда /help"""
        writer = kwargs["writer"]
        nick_name = kwargs["nick_name"]
        commands = kwargs["commands"]
        logger = kwargs["logger"]
        
        for command in commands:
            writer.write(f"[Сервер]: {command}\n".encode())
            await writer.drain()
            logger.info(f"Пользователь [{nick_name} запросил справку]")

    async def _handle_exit(self, **kwargs):
        """Команда /exit"""
        writer = kwargs["writer"]
        stop_event = kwargs["stop_event"]
        room_manager = kwargs["room_manager"]
        current_room = kwargs["current_room"]
        remove_user_from_system = kwargs["remove_user_from_system"]
        nick_name = kwargs["nick_name"]
        user_id = kwargs["user_id"]
        logger = kwargs["logger"]

        stop_event.set()
        await remove_user_from_system(room_manager, user_id)

        info = f"Пользователь [{nick_name}] вышел с сервера"
        await current_room.send_message(info, "Сервер", exclude_writer=writer)
        print(f"Пользователь [{nick_name}] вышел с сервера, используя команду /exit")
        logger.info(f"Пользователь {nick_name} вышел с сервера")

    async def _handle_connect(self, **kwargs):
        """Команда /connect [room_name]"""
        writer = kwargs["writer"]
        msg = kwargs["msg"]
        user_id = kwargs["user_id"]
        room_manager = kwargs["room_manager"]
        current_room = kwargs["current_room"]
        nick_name = kwargs["nick_name"]
        database_manager = kwargs["database_manager"]

        room_name = msg[9:]
        if await room_manager.check_room(room_name):
            leave_msg = f"Пользователь [{nick_name}] покинул комнату"
            await current_room.send_message(leave_msg, "Сервер", exclude_writer=writer)

            await room_manager.delete_user_from_rooms(user_id)
                            
            await room_manager.assign_user_to_room(writer, user_id, room_name, nick_name)

            current_room = await room_manager.get_room(room_name)

            messages = await database_manager.get_messages(room_name)
            for timestamp, sender, message in messages:
                formatted_msg = f"[{timestamp}][{sender}]: {message}\n"
                writer.write(formatted_msg.encode())
                await writer.drain()

            writer.write(f"✅ Вы присоединились к комнате [{room_name}]\n".encode())
            await writer.drain()

            connect_msg = f"Пользователь [{nick_name}] присоединился к комнате"
            await current_room.send_message(connect_msg, "Сервер", exclude_writer=writer)

        else:
            writer.write("❌ Такой комнаты не существует\n".encode())
            await writer.drain()

    async def _handle_leave(self, **kwargs):
        """Команда /leave"""
        writer = kwargs["writer"]
        user_id = kwargs["user_id"]
        room_manager = kwargs["room_manager"]
        current_room = kwargs["current_room"]
        nick_name = kwargs["nick_name"]
        database_manager = kwargs["database_manager"]

        if current_room.room == "general":
            writer.write("❌ Вы уже находитесь в главной комнате\n".encode())
            await writer.drain()
            return False

        leave_msg = f"Пользователь [{nick_name}] покинул комнату"
        await current_room.send_message(leave_msg, "Сервер", exclude_writer=writer)

        await room_manager.delete_user_from_rooms(user_id)
                    
        default_room = await room_manager.get_room("general")
        await room_manager.assign_user_to_room(writer, user_id, "general", nick_name)

        enter_msg = f"Пользователь [{nick_name}] вошел в главную комнату"
        await default_room.send_message(enter_msg, "Сервер", exclude_writer=writer)

        messages = await database_manager.get_messages(room_name="general")
        for timestamp, sender, message in messages:
            formatted_msg = f"[{timestamp}][{sender}]: {message}\n"
            writer.write(formatted_msg.encode())
            await writer.drain()

        writer.write("✅ Вы вернулись в главную комнату\n".encode())
        await writer.drain()

        return True
    
    async def _handle_rooms(self, **kwargs):
        """Команда /rooms"""
        writer = kwargs["writer"]
        room_manager = kwargs["room_manager"]

        all_rooms = await room_manager.get_rooms()
        rooms_list = "\n  • ".join(all_rooms)
        response = f"Доступные комнаты:\n  • {rooms_list}\n"
        writer.write(response.encode())
        await writer.drain()        

    async def _handle_login(self, **kwargs):
        """Команда /login [nick_name] [password]"""
        writer = kwargs["writer"]
        msg = kwargs["msg"]
        auth_manager = kwargs["auth_manager"]
        parts = msg.split()
        if len(parts) >= 3:
            username = parts[1]
            password = parts[2]

            if await auth_manager.authenticate(writer, username, password):
                writer.write(f"✅ Успешная аутентификация\n".encode())
                await writer.drain()  
            else:
                writer.write(f"❌ Неправильно введен логин или пароль\n".encode())
                await writer.drain()  
        else:
            writer.write(f"❌ Неправильный формат команды. Используйте: /login username password\n".encode())
            await writer.drain() 

    async def _handle_register(self, **kwargs):
        """Команда /register [nick_name] [password]"""
        writer = kwargs["writer"]
        msg = kwargs["msg"]
        auth_manager = kwargs["auth_manager"]

        parts = msg.split()
        if len(parts) >= 3:
            username = parts[1]
            password = parts[2]

            if await auth_manager.register(username, password):
                if await auth_manager.authenticate(writer, username, password):
                    writer.write(f"✅ Успешная регистрация и аутентификация\n".encode())
                    await writer.drain() 
                else:
                    writer.write(f"⚠️ Успешная регистрация, но ошибка аутентификации\n".encode())
                    await writer.drain() 
            else:
                writer.write(f"❌ Ошибка регистрации\n".encode())
                await writer.drain() 
        else:
            writer.write(f"❌ Неправильный формат команды. Используйте: /registr username password\n".encode())
            await writer.drain() 

    async def _handle_logout(self, **kwargs):
        """Команда /logout"""
        writer = kwargs["writer"]
        auth_manager = kwargs["auth_manager"]

        if auth_manager.is_authenticated(writer):
            auth_manager.logout(writer)
            writer.write(f"✅ Вы вышли из системы\n".encode())
            await writer.drain()
        else:
            writer.write(f"❌ Вы не были аутентифицированы\n".encode())
            await writer.drain()
        
