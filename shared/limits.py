from datetime import time


class RateLimiter:
    def __init__(self, max_messages_per_second=2.0, max_message_length = 10):
        self.max_messages_per_second = max_messages_per_second
        self.max_message_length = max_message_length
        self.user_timestamps = {}

    def can_send_message(self, writer, message):
        if len(message) > self.max_message_length:
            return False, f"Сообщение слишком длинное. Максимум: {self.max_message_length} символов"
        
        current_time = time.time()
        last_time = self.user_timestamps.get(writer)

        if last_time is not None:
            diff_time = current_time - last_time
            if diff_time < (1 / self.max_messages_per_second):
                return False, f"Превышена частота отправки сообщений"

        return True