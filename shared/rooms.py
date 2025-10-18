from shared.users import ListClients


class Room:
    def __init__(self, room_name):
        self.room = room_name
        self.users = ListClients()


class RoomManager:
    def __init__(self):
        self.rooms = {}

    def create_room(self, room_name):
        self.rooms[room_name] = Room(room_name)

    def delete_room(self, room_name):
        del self.rooms[room_name]

