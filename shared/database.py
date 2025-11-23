import aiosqlite


class DatabaseManager:
    def __init__(self, db_path="chat.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as con:
            cursor = con.cursor()

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS Messages(
                id INTEGER PRIMARY KEY,
                room_name TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL                       
            )
            """)
            
            await con.commit()

    async def save_message(self, room_name, sender, message, timestamp):
        async with aiosqlite.connect(self.db_path) as con:
            cursor = con.cursor()

            await cursor.execute("""
            INSERT INTO Messages (room_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?)
            """, (room_name, sender, message, timestamp))

            await con.commit()

    async def get_messages(self, room_name, limit=100):
        async with aiosqlite.connect(self.db_path) as con:
            cursor = con.cursor()

            await cursor.execute("""
            SELECT timestamp, sender, message FROM Messages 
            WHERE room_name = ?
            ORDER BY id DESC
            LIMIT ?
            """, (room_name, limit))


            messages = await cursor.fetchall()
            return messages