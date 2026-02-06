from shared.context import ServerContext


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
        # Создаем контекст из kwargs
        context = ServerContext(
            writer=kwargs["writer"],
            nick_name=kwargs["nick_name"],
            commands=kwargs["commands"],
            logger=kwargs["logger"]
        )

        for command in context.commands:
            context.writer.write(f"[Сервер]: {command}\n".encode())
            await context.writer.drain()
            context.logger.info(f"Пользователь [{context.nick_name} запросил справку]")

    async def _handle_exit(self, **kwargs):
        """Команда /exit"""
        # Создаем контекст из kwargs
        context = ServerContext(
            writer=kwargs["writer"],
            stop_event=kwargs["stop_event"],
            room_manager=kwargs["room_manager"],
            current_room=kwargs["current_room"],
            nick_name=kwargs["nick_name"],
            user_id=kwargs["user_id"],
            logger=kwargs["logger"],
            commands=kwargs["commands"]
        )
        remove_user_from_system = kwargs["remove_user_from_system"]

        context.stop_event.set()
        await remove_user_from_system(context.room_manager, context.user_id)

        info = f"Пользователь [{context.nick_name}] вышел с сервера"
        await context.current_room.send_message(info, "Сервер", exclude_writer=context.writer)
        print(f"Пользователь [{context.nick_name}] вышел с сервера, используя команду /exit")
        context.logger.info(f"Пользователь {context.nick_name} вышел с сервера")

    async def _handle_connect(self, **kwargs):
        """Команда /connect [room_name]"""
        # Создаем контекст из kwargs
        context = ServerContext(
            writer=kwargs["writer"],
            msg=kwargs["msg"],
            user_id=kwargs["user_id"],
            room_manager=kwargs["room_manager"],
            current_room=kwargs["current_room"],
            nick_name=kwargs["nick_name"],
            database_manager=kwargs["database_manager"],
            commands=kwargs["commands"],
            logger=kwargs["logger"]
        )

        room_name = context.msg[9:]
        if await context.room_manager.check_room(room_name):
            leave_msg = f"Пользователь [{context.nick_name}] покинул комнату"
            await context.current_room.send_message(leave_msg, "Сервер", exclude_writer=context.writer)

            await context.room_manager.delete_user_from_rooms(context.user_id)

            await context.room_manager.assign_user_to_room(context.writer, context.user_id, room_name, context.nick_name)

            current_room = await context.room_manager.get_room(room_name)

            messages = await context.database_manager.get_messages(room_name)
            for timestamp, sender, message in messages:
                formatted_msg = f"[{timestamp}][{sender}]: {message}\n"
                context.writer.write(formatted_msg.encode())
                await context.writer.drain()

            context.writer.write(f"✅ Вы присоединились к комнате [{room_name}]\n".encode())
            await context.writer.drain()

            connect_msg = f"Пользователь [{context.nick_name}] присоединился к комнате"
            await current_room.send_message(connect_msg, "Сервер", exclude_writer=context.writer)

        else:
            context.writer.write("❌ Такой комнаты не существует\n".encode())
            await context.writer.drain()

    async def _handle_leave(self, **kwargs):
        """Команда /leave"""
        # Создаем контекст из kwargs
        context = ServerContext(
            writer=kwargs["writer"],
            user_id=kwargs["user_id"],
            room_manager=kwargs["room_manager"],
            current_room=kwargs["current_room"],
            nick_name=kwargs["nick_name"],
            database_manager=kwargs["database_manager"],
            commands=kwargs["commands"],
            logger=kwargs["logger"]
        )

        if context.current_room.room == "general":
            context.writer.write("❌ Вы уже находитесь в главной комнате\n".encode())
            await context.writer.drain()
            return False

        leave_msg = f"Пользователь [{context.nick_name}] покинул комнату"
        await context.current_room.send_message(leave_msg, "Сервер", exclude_writer=context.writer)

        await context.room_manager.delete_user_from_rooms(context.user_id)

        default_room = await context.room_manager.get_room("general")
        await context.room_manager.assign_user_to_room(context.writer, context.user_id, "general", context.nick_name)

        enter_msg = f"Пользователь [{context.nick_name}] вошел в главную комнату"
        await default_room.send_message(enter_msg, "Сервер", exclude_writer=context.writer)

        messages = await context.database_manager.get_messages(room_name="general")
        for timestamp, sender, message in messages:
            formatted_msg = f"[{timestamp}][{sender}]: {message}\n"
            context.writer.write(formatted_msg.encode())
            await context.writer.drain()

        context.writer.write("✅ Вы вернулись в главную комнату\n".encode())
        await context.writer.drain()

        return True
    
    async def _handle_rooms(self, **kwargs):
        """Команда /rooms"""
        # Создаем контекст из kwargs
        context = ServerContext(
            writer=kwargs["writer"],
            room_manager=kwargs["room_manager"],
            commands=kwargs["commands"],
            logger=kwargs["logger"]
        )

        all_rooms = await context.room_manager.get_rooms()
        rooms_list = "\n  • ".join(all_rooms)
        response = f"Доступные комнаты:\n  • {rooms_list}\n"
        context.writer.write(response.encode())
        await context.writer.drain()        

    async def _handle_login(self, **kwargs):
        """Команда /login [nick_name] [password]"""
        # Создаем контекст из kwargs
        context = ServerContext(
            writer=kwargs["writer"],
            msg=kwargs["msg"],
            auth_manager=kwargs["auth_manager"],
            commands=kwargs["commands"],
            logger=kwargs["logger"]
        )

        parts = context.msg.split()
        if len(parts) >= 3:
            username = parts[1]
            password = parts[2]

            if await context.auth_manager.authenticate(context.writer, username, password):
                context.writer.write(f"✅ Успешная аутентификация\n".encode())
                await context.writer.drain()
            else:
                context.writer.write(f"❌ Неправильно введен логин или пароль\n".encode())
                await context.writer.drain()
        else:
            context.writer.write(f"❌ Неправильный формат команды. Используйте: /login username password\n".encode())
            await context.writer.drain()

    async def _handle_register(self, **kwargs):
        """Команда /register [nick_name] [password]"""
        # Создаем контекст из kwargs
        context = ServerContext(
            writer=kwargs["writer"],
            msg=kwargs["msg"],
            auth_manager=kwargs["auth_manager"],
            commands=kwargs["commands"],
            logger=kwargs["logger"]
        )

        parts = context.msg.split()
        if len(parts) >= 3:
            username = parts[1]
            password = parts[2]

            if await context.auth_manager.register(username, password):
                if await context.auth_manager.authenticate(context.writer, username, password):
                    context.writer.write(f"✅ Успешная регистрация и аутентификация\n".encode())
                    await context.writer.drain()
                else:
                    context.writer.write(f"⚠️ Успешная регистрация, но ошибка аутентификации\n".encode())
                    await context.writer.drain()
            else:
                context.writer.write(f"❌ Ошибка регистрации\n".encode())
                await context.writer.drain()
        else:
            context.writer.write(f"❌ Неправильный формат команды. Используйте: /registr username password\n".encode())
            await context.writer.drain()

    async def _handle_logout(self, **kwargs):
        """Команда /logout"""
        # Создаем контекст из kwargs
        context = ServerContext(
            writer=kwargs["writer"],
            auth_manager=kwargs["auth_manager"],
            commands=kwargs["commands"],
            logger=kwargs["logger"]
        )

        if context.auth_manager.is_authenticated(context.writer):
            context.auth_manager.logout(context.writer)
            context.writer.write(f"✅ Вы вышли из системы\n".encode())
            await context.writer.drain()
        else:
            context.writer.write(f"❌ Вы не были аутентифицированы\n".encode())
            await context.writer.drain()  
