Запуск сервера:
python -B -m server.main

Запуск клиента:
python -B -m client.main

Сборка в exe сервера:
pyinstaller --onefile --add-data "utils;utils" --add-data "shared;shared" --add-data "server;server" --name server_app server/main.py

Сборка в exe клиента:
pyinstaller --onefile --add-data "utils;utils" --add-data "shared;shared" --add-data "client;client" --name client_app client/main.py

Если код будет работать странно, то нужно очистить кэш:
    1) Для PowerShell:
        Remove-Item -Recurse -Force __pycache__
        Remove-Item -Recurse -Force server\__pycache__
        Remove-Item -Recurse -Force client\__pycache__
        Remove-Item -Recurse -Force utils\__pycache__
        Remove-Item -Recurse -Force shared\__pycache__

    2) Для Linux/Mac:
        rm -rf __pycache__
        rm -rf server/__pycache__
        rm -rf client/__pycache__
        rm -rf utils/__pycache__
        rm -rf shared/__pycache__

    3) Для Windows (Command Prompt):
        rmdir /s /q __pycache__
        rmdir /s /q server\__pycache__
        rmdir /s /q client\__pycache__
        rmdir /s /q utils\__pycache__
        rmdir /s /q shared\__pycache__
