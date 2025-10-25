from datetime import datetime

from shared.users import ListClients


class Room:
    def __init__(self, room_name):
        self.room = room_name
        self.users = ListClients()

    def add_users(self, writer, nick_name):
        self.users.add_user(writer, nick_name)

    def remove_users(self, writer):
        self.users.remove_user(writer)

    def get_users(self):
        return self.users.get_users()

    async def send_message(self, message, sender_name, exclude_writer=None):
        writers = self.users.get_users()
        time = datetime.now().strftime("%H:%M")
        for writer in writers:
            if writer is exclude_writer:
                continue
            writer.write(f"[{time}][{sender_name}]: {message}\n".encode())
            await writer.drain()


class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.user_rooms = {}

    def assign_user_to_room(self, writer, room):
        self.user_rooms[writer] = room

    def get_user_room(self, writer):
        return self.user_rooms.get(writer)
    
    def delete_user_from_rooms(self, writer):
        if writer in self.user_rooms:
            del self.user_rooms[writer]

    def create_room(self, room_name):
        self.rooms[room_name] = Room(room_name)

    def check_room(self, room_name):
        return room_name in self.rooms

    def get_room(self, room_name):
        if self.check_room(room_name):
            return self.rooms[room_name]
        return None

    def get_rooms(self):
        return self.rooms

    def delete_room(self, room_name):
        del self.rooms[room_name]