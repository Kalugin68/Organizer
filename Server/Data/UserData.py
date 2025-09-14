from . import ConnectDatabase
from tkinter import messagebox
import bcrypt


class UserDatabase(ConnectDatabase.Database):
    def __init__(self):
        super().__init__()

    def create_user_db(self, username, password):
        if self.connect_db():
            try:
                # Создаем таблицу, если её нет
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                                        id SERIAL PRIMARY KEY,
                                        username VARCHAR(30) NOT NULL,
                                        password TEXT NOT NULL)"""
                                    )
                print("[INFO] Таблица users создана или уже существует.")

                # Проверяем, существует ли пользователь
                self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                existing_user = self.cursor.fetchone()

                if existing_user is None:
                    # Добавляем нового пользователя
                    self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                    print("[INFO] Данные о пользователе добавлены.")
                    messagebox.showinfo("Успех", "Пользователь успешно зарегистрирован.")

                    return True

                else:
                    print(f"[INFO] Пользователь {username} уже существует.")
                    messagebox.showinfo("Информация", f"Пользователь {username} уже существует.")

                    return False

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")
                return False

            finally:
                self.close_connection()

    def check_user(self, username, password):
        """Проверяет, существует ли пользователь в базе данных (с bcrypt-проверкой)."""
        if self.connect_db():
            try:
                # Получаем хеш пароля пользователя
                self.cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                result = self.cursor.fetchone()

                if result:
                    hashed_password = result[0]
                    # Сверяем введённый пароль с хешем
                    if bcrypt.checkpw(password.encode(), hashed_password.encode()):
                        return True  # Успешная авторизация

                return False  # Неверный логин или пароль

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка при проверке пользователя: {ex}")
                return False

            finally:
                self.close_connection()

    def get_user_id(self, username):
        if self.connect_db():
            try:
                self.cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
                self.user_id = self.cursor.fetchone()

                if self.user_id is not None:
                    return self.user_id

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")

                return False

            finally:
                self.close_connection()

    def change_password(self, user_id, old_password, new_password):
        """Смена пароля пользователя в базе данных с учетом хеширования"""
        if self.connect_db():
            try:
                # Получаем текущий хеш пароля
                self.cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
                result = self.cursor.fetchone()

                if not result:
                    return False

                hashed_password = result[0]

                # Проверяем введённый текущий пароль
                if not bcrypt.checkpw(old_password.encode(), hashed_password.encode()):
                    return False

                # Хешируем новый пароль
                new_hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

                # Обновляем пароль
                self.cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_hashed_password, user_id))

                return True

            except Exception as e:
                print(f"[DB ERROR] Ошибка смены пароля: {e}")
                return False

            finally:
                self.close_connection()

    def get_user_stats(self, user_id):
        """Возвращает статистику активности пользователя"""
        if self.connect_db():
            try:
                # Подсчет задач
                self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s", (user_id,))
                task_count = self.cursor.fetchone()[0]

                # Подсчет заметок
                self.cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id = %s", (user_id,))
                note_count = self.cursor.fetchone()[0]

                # Подсчет контактов
                self.cursor.execute("SELECT COUNT(*) FROM contacts WHERE user_id = %s", (user_id,))
                contact_count = self.cursor.fetchone()[0]

                return {
                    "tasks": task_count,
                    "notes": note_count,
                    "contacts": contact_count
                }

            except Exception as e:
                print(f"[DB ERROR] Не удалось получить статистику: {e}")
                return None

            finally:
                self.close_connection()

