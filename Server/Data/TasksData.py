from . import ConnectDatabase
from tkinter import messagebox


class TasksDatabase(ConnectDatabase.Database):
    def __init__(self):
        super().__init__()

    def create_or_update_task_table(self, user_id, task, status):
        if self.connect_db():
            try:
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
                                        id SERIAL PRIMARY KEY,
                                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                                        task VARCHAR(200) NOT NULL,
                                        status VARCHAR(20) NOT NULL)"""
                                    )
                print("[INFO] Таблица tasks создана или уже существует.")

                self.cursor.execute("INSERT INTO tasks (user_id, task, status) VALUES (%s, %s, %s)",
                                    (user_id, task, status))

                return True

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")

                return False

            finally:
                self.close_connection()

    def delete_tasks_from_user_id(self, user_id):
        if self.connect_db():
            try:
                # Проверяем, есть ли задачи у пользователя
                self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s", (user_id,))
                task_count = self.cursor.fetchone()[0]

                # Удаляем все предыдущие задачи пользователя
                self.cursor.execute("DELETE FROM tasks WHERE user_id = %s", (user_id,))
                print(f"[INFO] Все задачи пользователя с id {user_id} были удалены.")

                return True

            except Exception as ex:
                print("[ERROR] У пользователя с id {user_id} нет задач для удаления!")

                return False

            finally:
                self.close_connection()

    def get_user_tasks(self, user_id):
        """Получение всех задач для пользователя по user_id"""
        if self.connect_db():
            try:
                # Получаем все задачи для данного пользователя
                self.cursor.execute("SELECT task, status FROM tasks WHERE user_id = %s;", (user_id,))
                tasks = self.cursor.fetchall()

                print(f"[INFO] Получены задачи для пользователя с id {user_id}: {tasks}")
                return tasks  # Возвращаем все задачи

            except Exception as ex:
                print("[ERROR] В базе данных нет задач для данного пользователя")
                return []

            finally:
                self.close_connection()
