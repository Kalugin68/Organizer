import threading
from Server import server   # твой server.py
from Client import MainWindow


def start_server():
    srv = server.Server()
    srv.start()  # предполагаю, что у тебя в классе есть метод start()


if __name__ == "__main__":
    # Запускаем сервер в отдельном потоке, чтобы он не блокировал GUI
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Запускаем клиентское окно
    app = MainWindow.MainWindow()
    app.mainloop()
