from datetime import datetime


class Room:
    def __init__(self, room_name, room_manager):
        self.room = room_name
        self.room_manager = room_manager

    async def send_message(self, message, sender_name, exclude_writer=None):
        users_in_room = await self.room_manager.get_users_in_room(self.room)

        time = datetime.now().strftime("%H:%M")

        for writer, nickname in users_in_room:
            if writer is exclude_writer:
                continue
            writer.write(f"[{time}][{sender_name}]: {message}\n".encode())
            await writer.drain()


class RoomManager:
    def __init__(self, database_manager):
        self.database_manager = database_manager
        self.user_connections = {}

    async def assign_user_to_room(self, writer, user_id, room_name, nick_name):
        await self.database_manager.add_user_to_room(room_name, user_id, nick_name)
        self.user_connections[user_id] = writer

    def get_user_connection(self, user_id):
        return self.user_connections.get(user_id)

    async def get_user_room(self, user_id):
        room_name = await self.database_manager.get_user_room(user_id)
        return room_name
    
    async def get_users_in_room(self, room_name):
        users_data = await self.database_manager.get_users_in_room(room_name)
        writers = []
        for user_id, nickname in users_data:
            writer = self.get_user_connection(user_id)
            if writer:
                writers.append((writer, nickname))
        return writers
    
    async def delete_user_from_rooms(self, user_id):
        await self.database_manager.remove_user_from_room(user_id)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def create_room(self, room_name):
        return await self.database_manager.create_room(room_name)

    async def check_room(self, room_name):
        return await self.database_manager.check_room(room_name)

    async def get_room(self, room_name):
        room_data = await self.database_manager.get_room(room_name)
        if room_data:
            return Room(room_name, self)
        return None

    async def get_rooms(self):
        return await self.database_manager.get_rooms()

    async def delete_room(self, room_name):
        await self.database_manager.delete_room(room_name)