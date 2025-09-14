from . import ConnectDatabase
from tkinter import messagebox


class NotesDatabase(ConnectDatabase.Database):
    def __init__(self):
        super().__init__()

    def create_or_update_notes_table(self, user_id, note_id, title, text):
        if self.connect_db():
            try:
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS notes (
                                        id UUID PRIMARY KEY,
                                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                                        title TEXT NOT NULL,
                                        text TEXT NOT NULL)"""
                                    )
                print("[INFO] Таблица notes создана или уже существует.")

                self.cursor.execute("INSERT INTO notes (id, user_id, title, text) VALUES (%s, %s, %s, %s)",
                                    (note_id, user_id, title, text))

                return True

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")

                return False

            finally:
                self.close_connection()

    def get_notes_from_db(self, user_id):
        """Возвращает список заметок пользователя по его ID."""
        if self.connect_db():
            try:
                self.cursor.execute("SELECT id, title, text FROM notes WHERE user_id = %s", (user_id,))
                notes = self.cursor.fetchall()

                print(f"[INFO] Получены заметки для пользователя {user_id}: {notes}")

                return notes

            except Exception as ex:
                print(f"[ERROR] Ошибка при получении заметок: {ex}")

                return []

            finally:
                self.close_connection()

    def delete_user_note(self, note_id):
        """Удаляет заметку по ID"""
        if self.connect_db():
            try:
                self.cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))

                return True

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")

                return False

            finally:
                self.close_connection()

    def update_user_note(self, note_id, new_title, new_text):
        """Обновляет заметку по ID"""
        if self.connect_db():
            try:
                self.cursor.execute("UPDATE notes SET title = %s, text = %s WHERE id = %s",
                                    (new_title, new_text, note_id))

                return True

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")

                return False

            finally:
                self.close_connection()
