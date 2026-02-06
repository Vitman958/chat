class ServerContext:
    """
    Класс контекста для передачи всех необходимых данных сервера
    """
    
    def __init__(
        self,
        server_name: str = "",
        reader = None,
        writer = None,
        nick_name: str = "",
        user_id: str = "",
        stop_event = None,
        room_manager = None,
        rate_limiter = None,
        command_handler = None,
        database_manager = None,
        auth_manager = None,
        current_room = None,
        msg: str = "",
        commands = None,
        logger = None
    ):
        self.server_name = server_name
        self.reader = reader
        self.writer = writer
        self.nick_name = nick_name
        self.user_id = user_id
        self.stop_event = stop_event
        self.room_manager = room_manager
        self.rate_limiter = rate_limiter
        self.command_handler = command_handler
        self.database_manager = database_manager
        self.auth_manager = auth_manager
        self.current_room = current_room
        self.msg = msg
        self.commands = commands
        self.logger = logger

    def copy_with(self, **updates):
        """
        Создает копию контекста с обновленными значениями
        """
 
        new_context = ServerContext(
            server_name=self.server_name,
            reader=self.reader,
            writer=self.writer,
            nick_name=self.nick_name,
            user_id=self.user_id,
            stop_event=self.stop_event,
            room_manager=self.room_manager,
            rate_limiter=self.rate_limiter,
            command_handler=self.command_handler,
            database_manager=self.database_manager,
            auth_manager=self.auth_manager,
            current_room=self.current_room,
            msg=self.msg,
            commands=self.commands,
            logger=self.logger
        )
    
        for attr, value in updates.items():
            setattr(new_context, attr, value)
        return new_context
