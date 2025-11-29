class AuthManager:
    def __init__(self, database_manager):
        self.database_manager = database_manager
        self.auth_users = {}
        self.auth_writers = set()

    async def authenticate(self, writer, nick_name, password):
        if await self.database_manager.verify_user(nick_name, password):
            self.auth_users[writer] = nick_name
            self.auth_writers.add(writer)
            return True
        else:
            return False

    def is_authenticated(self, writer):
        return writer in self.auth_users
        
    def logout(self, writer):
        if writer in self.auth_users:
            del self.auth_users[writer]
            self.auth_writers.remove(writer)

    async def register(self, nick_name, password):
        try:
            await self.database_manager.save_user(nick_name, password)
            return True
        except Exception as e:
            print(f"Ошибка регистрации: {e}")
            return False