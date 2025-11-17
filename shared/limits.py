class RateLimiter:
    def __init__(self, max_messages_per_second=2.0, max_message_length = 10):
        self.max_messages_per_second = max_messages_per_second
        self.max_message_length = max_message_length
        self.user_timestamps = {}

    