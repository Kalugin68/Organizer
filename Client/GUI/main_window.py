import customtkinter as ctk
from PIL import Image, ImageDraw
from Client.GUI.MainPages import contact_page, notes_page, settings_page, tasks_page
from Client.Responses.main_responses import *
import os


# ====== Главное окно (органайзер) ======
class OrganizerWindow(ctk.CTkToplevel):
    def __init__(self, username, master, client, authorization):
        """Создает главное окно органайзера"""
        super().__init__()
        ctk.set_appearance_mode("light")  # Установка темы (Light/Dark)
        ctk.set_default_color_theme("green")  # Установка цветовой схемы

        self.withdraw()  # Скрываем окно в начале, чтобы избежать мигания
        self.authorization = authorization
        self.master = master
        self.client = client
        self.user_id = None
        self.username = username

        # Получаем размеры экрана и центрируем окно
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 1000
        window_height = 505
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.__login_name = username

        self.title("Сетевой органайзер")
        self.geometry("800x600")


        # === Основной макет ===
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # === Навигационная панель ===
        self.nav_frame = ctk.CTkFrame(self.main_frame, width=200)
        self.nav_frame.pack(side="left", fill="y")

        # === Попытка загрузить пользовательский аватар ===
        custom_path = f"Client/Images/Avatars/user_{get_user_id(self.client, self.username, self.user_id)}.jpg"
        if os.path.exists(custom_path):
            self.image_author = Image.open(custom_path)
        else:
            self.image_author = Image.open("Client/Images/author.jpg")

        # === Аватар пользователя ===
        self.rounded_image_author = self.round_image(self.image_author, 1320)  # Делаем изображение круглым
        self.image_author_tk = ctk.CTkImage(size=(80, 80), light_image=self.rounded_image_author,
                                            dark_image=self.rounded_image_author)

        self.image_author_label = ctk.CTkLabel(self.nav_frame, text="", image=self.image_author_tk)
        self.image_author_label.pack(padx=10, pady=5)

        self.login_label = ctk.CTkLabel(self.nav_frame, text=self.get_login_name(), font=("Arial", 14))
        self.login_label.pack(padx=10, pady=5)

        # === Кнопки навигации ===
        self.nav_buttons = {
            "Задачи": ctk.CTkButton(self.nav_frame, text="📋 Задачи", command=lambda: self.show_frame("tasks")),
            "Заметки": ctk.CTkButton(self.nav_frame, text="📝 Заметки", command=lambda: self.show_frame("notes")),
            "Контакты": ctk.CTkButton(self.nav_frame, text="👥 Контакты", command=lambda: self.show_frame("contacts")),
            "Настройки": ctk.CTkButton(self.nav_frame, text="⚙️ Настройки", command=lambda: self.show_frame("settings"))
        }

        for btn in self.nav_buttons.values():
            btn.pack(fill="x", padx=10, pady=5)

        # === Контентная область ===
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # === Получение ID пользователя ===
        self.user_id = get_user_id(self.client, self.username, self.user_id)

        # === Создание страниц ===
        self.frames = {
            "tasks": tasks_page.TasksPage(self.content_frame, self.client, self.user_id).create_tasks_page(),
            "notes": notes_page.NotePage(self.content_frame, self.client, self.user_id).create_notes_page(),
            "contacts": contact_page.ContactPage(self.content_frame, self.client, self.user_id).create_contacts_page(),
            "settings": settings_page.SettingsPage(self.content_frame, self.client, self.user_id,
                                                   self.username, self, self.authorization).create_settings_page()
        }

        self.after(200, self.show_main_window)  # Даем время на загрузку перед показом окна

        # Закрываем главное окно при закрытии этого окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_main_window(self):
        """Отображает окно после полной загрузки интерфейса"""
        self.show_frame("tasks")  # Загружаем экран "Задачи" по умолчанию
        self.deiconify()  # Показываем окно

    def get_login_name(self):
        """Возвращает логин пользователя"""
        return self.__login_name

    def show_frame(self, name):
        """Отображает нужную страницу"""
        for frame in self.frames.values():
            frame.pack_forget()  # Скрываем все страницы

        self.frames[name].pack(fill="both", expand=True)  # Показываем нужную страницу

    def round_image(self, image_main, radius):
        """Закругляет углы изображения"""
        image_main = image_main.convert("RGBA")  # Конвертируем в формат с прозрачностью
        width, height = image_main.size

        # Создаем маску
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)

        # Добавляем маску к изображению
        image_main.putalpha(mask)

        return image_main

    def update_avatar(self, image_path):
        """Обновляет изображение аватара в навигационной панели"""
        try:
            new_image = Image.open(image_path)
            rounded = self.round_image(new_image, 1320)
            new_ctk_img = ctk.CTkImage(size=(80, 80), light_image=rounded, dark_image=rounded)

            self.image_author_label.configure(image=new_ctk_img)
            self.image_author_label.image = new_ctk_img  # Чтобы не сборщик мусора не удалил

        except Exception as e:
            print(f"[AVATAR ERROR] Не удалось обновить аватар: {e}")

    def on_close(self):
        """Закрывает основное окно при выходе"""
        if self.master:
            self.master.destroy()
