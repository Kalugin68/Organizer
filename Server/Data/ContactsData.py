from . import ConnectDatabase
from tkinter import messagebox


class ContactsDatabase(ConnectDatabase.Database):
    def __init__(self):
        super().__init__()

    def create_or_update_contacts_table(self, user_id, name, surname, phone, email):
        """Создание таблицы контактов (общая для всех пользователей)"""
        if self.connect_db():
            try:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        name TEXT NOT NULL,
                        surname TEXT,
                        phone TEXT,
                        email TEXT
                    )
                """)

                self.cursor.execute(
                    "INSERT INTO contacts (user_id, name, surname, phone, email) VALUES (%s,%s,%s,%s,%s)",
                    (user_id, name, surname, phone, email)
                )

                return True

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")

                return False

            finally:
                self.close_connection()

    def get_contacts(self, user_id):
        """Получение всех контактов пользователя"""
        if self.connect_db():
            try:
                self.cursor.execute(
                    "SELECT id, name, surname, phone, email FROM contacts WHERE user_id = %s",
                    (user_id,)
                )
                return self.cursor.fetchall()

            except Exception as ex:
                print(f"[ERROR] Ошибка при получении контактов: {ex}")

                return []

            finally:
                self.close_connection()

    def delete_contact(self, contact_id):
        """Удаление контакта по его ID"""
        if self.connect_db():
            try:
                self.cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
                return True

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")

                return False

            finally:
                self.close_connection()

    def update_contact(self, contact_id, name, surname, phone, email):
        """Обновление информации о контакте"""
        if self.connect_db():
            try:
                self.cursor.execute("""
                    UPDATE contacts
                    SET name = %s, surname = %s, phone = %s, email = %s
                    WHERE id = %s
                """, (name, surname, phone, email, contact_id))

                return True

            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")

                return False

            finally:
                self.close_connection()