import aiosqlite


class DatabaseManager:
    def __init__(self, db_path="chat.db"):
        self.db_path = db_path

    async def init_db(self):
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
            
            await con.commit()

    async def save_message(self, room_name, sender, message, timestamp):
        async with aiosqlite.connect(self.db_path) as con:

            await con.execute("""
            INSERT INTO Messages (room_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?)
            """, (room_name, sender, message, timestamp))

            await con.commit()

    async def get_messages(self, room_name, limit=100):
        async with aiosqlite.connect(self.db_path) as con:
            cursor = await con.execute("""
            SELECT timestamp, sender, message FROM Messages 
            WHERE room_name = ?
            ORDER BY id DESC
            LIMIT ?
            """, (room_name, limit))

            messages = await cursor.fetchall()
            return messages
        
    async def save_user(self, nick_name, password_hash):
        async with aiosqlite.connect(self.db_path) as con:

            await con.execute("""
            INSERT INTO Users (username, password_hash)
            VALUES (?, ?)
            """, (nick_name, password_hash))

            await con.commit