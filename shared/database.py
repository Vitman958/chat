import aiosqlite


class DatabaseManager:
    def __init__(self, db_path="chat.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as con:

            await con.execute("""
            CREATE TABLE IF NOT EXISTS messages(
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

            await con.execute("""
            INSERT INTO messages (room_name, sender, message, timestamp)
            VALUES (?, ?, ?, ?)
            """, (room_name, sender, message, timestamp))

            await con.commit()