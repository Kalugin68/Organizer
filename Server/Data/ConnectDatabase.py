from tkinter import messagebox
import psycopg2

class Database:

    def connect_db(self):
        self.connection = None
        self.cursor = None

        try:
            # Соединение с БД
            self.connection = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="123456",
                host="127.0.0.1",
                port="5432"
            )

            self.connection.autocommit = True
            self.cursor = self.connection.cursor()

            return True

        except Exception as ex:
            messagebox.showerror("Ошибка", f"Ошибка работы с PostgreSQL: {ex}")
            return False

    def close_connection(self):
        """Закрытие соединения"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("[INFO] PostgreSQL соединение закрыто")