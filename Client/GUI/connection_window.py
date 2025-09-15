import customtkinter as ctk
from Client.client import Client
from Client.GUI import authorization_window


class ConnectionWindow(ctk.CTk):
    def __init__(self):
        """Главное окно для подключения к серверу"""
        super().__init__()
        ctk.set_appearance_mode("light")  # Установка темы (Light/Dark)
        ctk.set_default_color_theme("green")  # Установка цветовой схемы

        self.my_client = None  # Переменная для хранения клиента

        self.title("Подключение к серверу")
        self.geometry("400x300")

        # Поля ввода для IP-адреса и порта
        self.ip_entry = ctk.CTkEntry(self, placeholder_text="Введите IP-адрес сервера или имя хоста", width=260)
        self.ip_entry.pack(pady=10)
        self.ip_entry.bind('<Return>', lambda event: self.connect_to_server())
        # Кнопка подключения
        self.connect_button = ctk.CTkButton(self, text="Подключиться", command=self.connect_to_server, width=170)
        self.connect_button.pack(pady=20)

        # Метка для вывода ошибок
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.pack()

    def connect_to_server(self):
        """Попытка подключения к серверу"""
        ip = self.ip_entry.get()

        self.my_client = Client(ip)  # Создаем клиентский объект

        if self.my_client.connect():  # Проверяем успешность подключения
            try:
                # Если подключение успешно — выводим сообщение и запускаем окно авторизации
                self.status_label.configure(text="Подключение успешно!", text_color="green")
                self.after(1000, self.open_auth_window)  # Пауза перед открытием окна авторизации

            except Exception as e:
                # В случае ошибки выводим сообщение
                self.status_label.configure(text=f"Ошибка подключения: {e}", text_color="red")

    def open_auth_window(self):
        """Открытие окна авторизации"""
        self.withdraw()  # Скрываем главное окно
        auth_window = authorization_window.AuthorizationWindow(self.my_client, self)
        auth_window.mainloop()  # Запускаем цикл событий для окна авторизации

