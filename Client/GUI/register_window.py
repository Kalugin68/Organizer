import customtkinter as ctk
from Client.User import password_hasher
from Client.Responses.main_responses import *

# ====== Окно регистрации ======
class RegisterWindow(ctk.CTkToplevel):
    def __init__(self, client):
        """Создает окно регистрации"""
        super().__init__()
        ctk.set_appearance_mode("light")  # Установка темы (Light/Dark)
        ctk.set_default_color_theme("green")  # Установка цветовой схемы

        self.client = client

        self.__username = None
        self.__password = None
        self.__correct_password = None

        # Получаем размеры экрана и устанавливаем окно по центру экрана
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 550
        window_height = 505
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.title("Регистрация")
        self.geometry("400x350")

        # Основной фрейм
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=40, fill="both", expand=True)

        # Заголовок
        ctk.CTkLabel(self.frame, text="Регистрация", font=("Arial", 20)).pack(pady=10)

        # Поле ввода логина
        self.new_username_entry = ctk.CTkEntry(self.frame, placeholder_text="Придумайте логин")
        self.new_username_entry.pack(pady=5)

        # Поле ввода пароля
        self.new_password_entry = ctk.CTkEntry(self.frame, placeholder_text="Придумайте пароль", show="*")
        self.new_password_entry.pack(pady=5)

        # Фрейм для второго ввода пароля и кнопки "Глаз"
        self.password_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.password_frame.pack(pady=5, fill="x")

        # Поле подтверждения пароля
        self.second_password_entry = ctk.CTkEntry(self.password_frame, placeholder_text="Повторите пароль", show="*")
        self.second_password_entry.pack(padx=(89, 5), pady=5, side="left")

        # Кнопка скрытия/отображения пароля
        self.show_password = False
        self.toggle_button = ctk.CTkButton(self.password_frame, text="👁", width=10, command=self.toggle_password)
        self.toggle_button.pack(side="left")

        # Кнопка регистрации
        self.register_button = ctk.CTkButton(self.frame, text="Зарегистрироваться", command=self.register_user)
        self.register_button.pack(pady=10)

        # Метка для вывода ошибок
        self.error_label = ctk.CTkLabel(self.frame, text="", text_color="red")
        self.error_label.pack(pady=10)

    def register_user(self):
        """Обработка регистрации пользователя"""
        self.set_username(self.new_username_entry.get().strip())
        self.set_password(self.new_password_entry.get().strip())
        self.set_correct_password(self.second_password_entry.get().strip())

        # Проверка на пустые поля
        if not self.get_username() or not self.get_password() or not self.get_correct_password():
            self.error_label.configure(text="Введите логин и пароль!", text_color="red")
            return

        # Вызов функции, которая отправляет запрос на сервер
        if send_new_profile(self.client, self.get_username(),
                            self.get_password(), self.get_correct_password()) == "OK":
            self.error_label.configure(text="Профиль создан!", text_color="green")
            self.destroy()  # Закрываем окно регистрации
        elif send_new_profile(self.client, self.get_username(),
                            self.get_password(), self.get_correct_password()) == "PROFILE EXISTS":
            self.error_label.configure(text="Данный аккаунт уже существует!", text_color="red")
        else:
            self.error_label.configure(text="Пароли не совпадают!", text_color="red")

    def toggle_password(self):
        """Переключение видимости пароля"""
        self.show_password = not self.show_password
        self.new_password_entry.configure(show="" if self.show_password else "*")
        self.second_password_entry.configure(show="" if self.show_password else "*")

    # Методы для работы с защищёнными полями
    def get_username(self):
        return self.__username

    def set_username(self, username):
        self.__username = username

    def get_password(self):
        return self.__password

    def set_password(self, password):
        self.__password = password

    def get_correct_password(self):
        return self.__correct_password

    def set_correct_password(self, correct_password):
        self.__correct_password = correct_password
