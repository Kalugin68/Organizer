import socket


class Client:
    def __init__(self, host):
        self.host = host

    def connect(self):
        """Установление соединения с сервером"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, 10000))
            return True
        except Exception as e:
            print(f"Ошибка соединения с сервером: {e}")
            return False

    def send_data(self, message):
        """Отправка данных на сервер"""
        try:
            if not self.client_socket:
                raise ConnectionError("Клиент не подключен к серверу")

            self.client_socket.send(message.encode("utf-8"))
            response = self.client_socket.recv(1024).decode("utf-8")  # Получаем ответ

            if response == "FAIL":
                print("[CLIENT] Ошибка входа, пробуем снова...")

            return response  # Возвращаем ответ сервера

        except Exception as e:
            print(f"[CLIENT ERROR] Ошибка при отправке данных: {e}")

            return "ERROR"