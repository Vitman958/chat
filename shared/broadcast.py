import asyncio
from datetime import datetime


async def broadcast(message, users, sender_name, exclude_writer=None):
    writers = users.get_users()
    time = datetime.now().strftime("%H:%M")
    for writer in writers:
        if writer is exclude_writer:
            continue
        writer.write(f"[{time}][{sender_name}]: {message}\n".encode())
        await writer.drain()