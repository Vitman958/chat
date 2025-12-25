from aioconsole import ainput

async def handle_read(reader, stop_event):
    """Чтение сообщений от сервера"""
    while True:
        data = await reader.readline()
        if not data or stop_event.is_set():
            break
        print(data.decode().strip())


async def handle_write(writer, stop_event):
    """Отправка сообщений серверу"""
    while True:
        try:
            msg = await ainput()
            if msg == "/exit":
                writer.write(f"{msg}\n".encode())
                print("Выход с сервера")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                stop_event.set()
                break
            
            writer.write(f"{msg}\n".encode())
            await writer.drain()

        except ConnectionResetError:
            print("❌ Разоравно соединение с сервером")
            stop_event.set()
            break 