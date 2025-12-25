import aiosqlite

from shared.security import hash_password, verify_password


class DatabaseManager:
    def __init__(self, db_path="chat.db"):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация Базы Данных"""
        async with aiosqlite.connect(self.db_path) as con:

            await con.execute("""
            CREATE TABLE IF NOT EXISTS Messages(
                id INTEGER PRIMARY KEY,
                room_name TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL                       
            )
            """)

            await con.execute("""
            CREATE TABLE IF NOT EXISTS Users(
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            await con.execute("""
            CREATE TABLE IF NOT EXISTS Rooms(
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            await con.execute("""
            CREATE TABLE IF NOT EXISTS RoomUsers(
                id INTEGER PRIMARY KEY,
                room_name TEXT NOT NULL,
                writer_address TEXT NOT NULL,
                nickname TEXT NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_name) REFERENCES Rooms(name)
            )
            """)
            
            await con.commit()

    async def save_message(self, room_name, sender, message, timestamp):
        """Сохранение сообщений"""
        async with aiosqlite.connect(self.db_path) as con:

            await con.execute("""
            INSERT INTO Messages (room_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?)
            """, (room_name, sender, message, timestamp))

            await con.commit()

    async def get_messages(self, room_name, limit=100):
        """Получение сообщений"""
        async with aiosqlite.connect(self.db_path) as con:
            cursor = await con.execute("""
            SELECT timestamp, sender, message FROM Messages 
            WHERE room_name = ?
            ORDER BY id ASC
            LIMIT ?
            """, (room_name, limit))

            messages = await cursor.fetchall()
            return messages
        
    async def save_user(self, nick_name, password):
        """Сохранение пользователя"""
        password_hash = hash_password(password)

        async with aiosqlite.connect(self.db_path) as con:

            await con.execute("""
            INSERT INTO Users (username, password_hash)
            VALUES (?, ?)
            """, (nick_name, password_hash))

            await con.commit()

    async def verify_user(self, nick_name, password):
        """Верификация пользователя"""

        async with aiosqlite.connect(self.db_path) as con:
            cursor = await con.execute("""
            SELECT password_hash FROM Users
            WHERE username = ?
            """, (nick_name,))

            user = await cursor.fetchone()
            if user is None:
                return False

            password_hash = user[0]

            return verify_password(password, password_hash)
        
    async def create_room(self, room_name):
        """Создание комнаты"""
        async with aiosqlite.connect(self.db_path) as con:
            try:
                await con.execute("""
                INSERT INTO Rooms (name) VALUES (?)
                """, (room_name,))
                await con.commit()
                return True
            
            except Exception as e:
                print(f"Ошибка создания комнаты: {e}")
                return False
            
    async def check_room(self, room_name):
        """Проверка на существование комнаты"""
        async with aiosqlite.connect(self.db_path) as con:
            cursor = await con.execute("""
                SELECT COUNT(*) FROM Rooms WHERE name = ?
            """, (room_name,))

            count = await cursor.fetchone()
            return count[0] > 0    
            
    async def get_room(self, room_name):
        """Получние комнаты"""
        async with aiosqlite.connect(self.db_path) as con:
            cursor = await con.execute("""
                SELECT name FROM Rooms WHERE name = ?
            """, (room_name,))

            room = await cursor.fetchone()
            return room[0] if room else None
        
    async def get_rooms(self):
        """Получение списка комнаты"""
        async with aiosqlite.connect(self.db_path) as con:
            cursor = await con.execute("""
                SELECT name FROM Rooms
            """)

            rooms = await cursor.fetchall()
            return [room[0] for room in rooms]
        
    async def delete_room(self, room_name):
        """Удаление комнаты"""
        async with aiosqlite.connect(self.db_path) as con:
            await con.execute("""
                DELETE FROM Rooms WHERE name = ?
            """, (room_name,))
            await con.commit()

    async def add_user_to_room(self, room_name, user_id, nickname):
        """Добавление пользователя в комнату"""
        async with aiosqlite.connect(self.db_path) as con:
            await con.execute("""
                INSERT INTO RoomUsers (room_name, writer_address, nickname)
                VALUES (?, ?, ?)
            """, (room_name, user_id, nickname))
            await con.commit()

    async def remove_user_from_room(self, user_id):
        """Удаления пользователя из комнаты"""
        async with aiosqlite.connect(self.db_path) as con:
            await con.execute("""
                DELETE FROM RoomUsers WHERE writer_address = ?
            """, (user_id,))
            await con.commit()

    async def get_users_in_room(self, room_name):
        """Получение пользователей в комнате"""
        async with aiosqlite.connect(self.db_path) as con:
            cursor = await con.execute("""
                SELECT writer_address, nickname FROM RoomUsers WHERE room_name = ?
            """, (room_name,))
            return await cursor.fetchall()
        
    async def get_user_room(self, user_id):
        """Получение комнаты пользователя"""
        async with aiosqlite.connect(self.db_path) as con:
            cursor = await con.execute("""
                SELECT room_name FROM RoomUsers WHERE writer_address = ?
            """, (user_id,))
            result = await cursor.fetchone()
        return result[0] if result else None
    
    async def check_user_exists(self, nick_name):
        """Проверка пользователя в системе"""
        async with aiosqlite.connect(self.db_path) as con:
            cursor = await con.execute("""
                SELECT COUNT(*) FROM Users WHERE username = ?
            """, (nick_name,))
            count = await cursor.fetchone()
            return count[0] > 0