import customtkinter as ctk
from tkinter import messagebox
import os
from tkinter import filedialog
from PIL import Image


class SettingsPage:
    def __init__(self, parent_frame, client, user_id, username, main_window, authorization):
        """Создаем менеджер заметок внутри переданного родительского виджета"""
        self.parent_frame = parent_frame
        self.client = client
        self.user_id = user_id
        self.username = username
        self.main_window = main_window
        self.authorization = authorization

    def create_settings_page(self):
        frame = ctk.CTkFrame(self.parent_frame)
        frame.pack(fill="both", expand=True, padx=40, pady=30)

        # 🔹 Заголовок
        ctk.CTkLabel(frame, text="Настройки", font=("Arial", 20, "bold")).pack(pady=(0, 20))

        # 🔹 Фрейм с информацией о пользователе
        info_frame = ctk.CTkFrame(frame, corner_radius=10)
        info_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(info_frame, text=f"Логин: {self.username}", font=("Arial", 14)).pack(pady=10)

        # 🔹 Фрейм со статистикой активности
        stats_frame = ctk.CTkFrame(frame, corner_radius=10)
        stats_frame.pack(fill="x", pady=10)

        # Загрузка статуса активности
        stats = self.load_stats()
        ctk.CTkLabel(stats_frame, text="Статистика активности", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(stats_frame, text=f"Задач создано: {stats.get('tasks')}", font=("Arial", 12)).pack()
        ctk.CTkLabel(stats_frame, text=f"Заметок: {stats.get('notes')}", font=("Arial", 12)).pack()
        ctk.CTkLabel(stats_frame, text=f"Контактов: {stats.get('contacts')}", font=("Arial", 12)).pack()

        # 🔹 Фрейм с настройками
        settings_frame = ctk.CTkFrame(frame, corner_radius=10)
        settings_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(settings_frame, text="Настройки", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        change_pass_btn = ctk.CTkButton(settings_frame, text="Сменить пароль", command=self.change_password)
        change_pass_btn.pack(pady=5)

        # 🔹 Кнопка загрузки аватара
        upload_avatar_btn = ctk.CTkButton(settings_frame, text="Загрузить аватар", command=self.upload_avatar)
        upload_avatar_btn.pack(pady=5)

        ctk.CTkLabel(settings_frame, text="Тема оформления:", font=("Arial", 12)).pack(pady=(10, 2))
        theme_select = ctk.CTkComboBox(settings_frame, values=["Светлая", "Темная"], command=self.change_theme)
        theme_select.set("Светлая")  # Значение по умолчанию
        theme_select.pack(pady=5)

        # 🔹 Кнопка выхода
        logout_button = ctk.CTkButton(frame, text="Выйти из аккаунта", fg_color="red", command=self.logout)
        logout_button.pack(pady=20)

        return frame

    def change_password(self):
        """Открывает окно смены пароля"""

        window = ctk.CTkToplevel(self.parent_frame)
        window.title("Смена пароля")
        window.geometry("400x300")
        window.grab_set()  # Блокируем родительское окно

        # Получаем размеры экрана и центрируем окно
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_width = 400
        window_height = 300
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        ctk.CTkLabel(window, text="Текущий пароль:", anchor="w").pack(pady=(20, 5), padx=20, fill="x")
        old_pass = ctk.CTkEntry(window, show="*")
        old_pass.pack(padx=20, fill="x")

        ctk.CTkLabel(window, text="Новый пароль:", anchor="w").pack(pady=(15, 5), padx=20, fill="x")
        new_pass = ctk.CTkEntry(window, show="*")
        new_pass.pack(padx=20, fill="x")

        ctk.CTkLabel(window, text="Подтвердите новый пароль:", anchor="w").pack(pady=(15, 5), padx=20, fill="x")
        confirm_pass = ctk.CTkEntry(window, show="*")
        confirm_pass.pack(padx=20, fill="x")

        def submit():
            old = old_pass.get()
            new = new_pass.get()
            confirm = confirm_pass.get()

            if not old or not new or not confirm:
                messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля.")
                return

            if new != confirm:
                messagebox.showerror("Ошибка", "Новые пароли не совпадают.")
                return

            # Отправляем на сервер
            message = f"CHANGE_PASSWORD;{self.user_id};{old};{new}"
            if self.client.connect():
                response = self.client.send_data(message)

                if response == "SUCCESS":
                    messagebox.showinfo("Успех", "Пароль успешно изменён.")
                    window.destroy()
                elif response == "INVALID_PASSWORD":
                    messagebox.showerror("Ошибка", "Неверный текущий пароль.")
                else:
                    messagebox.showerror("Ошибка", "Не удалось сменить пароль. Попробуйте позже.")

        ctk.CTkButton(window, text="Сменить пароль", command=submit).pack(pady=20)

    def load_stats(self):
        """Запрашивает статистику у сервера"""
        if self.client.connect():
            try:
                response = self.client.send_data(f"GET_STATS;{self.user_id}")

                if response == "NO_DATA":
                    return {"tasks": 0, "notes": 0, "contacts": 0}
                elif response == "ERROR":
                    return {"tasks": "-", "notes": "-", "contacts": "-"}

                # Преобразуем строку вида tasks:12;notes:5;contacts:3
                parts = response.split(";")
                stats = {part.split(":")[0]: int(part.split(":")[1]) for part in parts}
                return stats

            except Exception as e:
                print(f"[CLIENT] Ошибка загрузки статистики: {e}")
                return {"tasks": "-", "notes": "-", "contacts": "-"}

    def change_theme(self, theme_name):
        """Смена темы оформления"""
        if theme_name == "Темная":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def logout(self):
        """Функция выхода из аккаунта"""
        self.main_window.destroy()  # Закрываем главное окно
        self.authorization.deiconify()

    def upload_avatar(self):
        """Открывает диалог выбора изображения и обновляет аватар"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )

        if not file_path:
            return  # Отмена выбора

        try:
            # Сохраняем выбранное изображение в папку пользователя
            save_dir = "Client/Images/Avatars"
            os.makedirs(save_dir, exist_ok=True)
            ext = os.path.splitext(file_path)[-1]
            saved_path = os.path.join(save_dir, f"user_{self.user_id}{ext}")

            # Открываем, уменьшаем, сохраняем
            image = Image.open(file_path)
            image = image.resize((80, 80))
            image.save(saved_path)

            messagebox.showinfo("Успех", "Аватар успешно обновлён.")

            # Обновим аватар в главном окне
            self.main_window.update_avatar(saved_path)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
