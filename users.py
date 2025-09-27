class ListClients:
    def __init__(self):
        self.users = {}
        self.writers = set()

    def add_user(self, writer, nick_name):
        self.writers.add(writer)
        self.users[writer] = nick_name
    
    def remove_user(self, writer):
        self.writers.remove(writer)
        del self.users[writer]

    def check_user(self, nick_name):
        if nick_name in self.users.values():
            return False
        else:
            return True

    def get_users(self):
        return self.writers
    
    def get_user(self, writer):
        if writer is None:
            return 
        return self.users[writer]