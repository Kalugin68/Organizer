import socket
import threading
from .Data import (UserData)
from .Data import TasksData
from .Data import NotesData
from .Data import ContactsData


class Server:
    def __init__(self, host="0.0.0.0", port=10000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[SERVER] Запущен на {self.host}:{self.port}")

        self.db_user = UserData.UserDatabase()  # Создаём объект БД без лишних параметров
        self.db_tasks = TasksData.TasksDatabase()
        self.db_notes = NotesData.NotesDatabase()
        self.db_contacts = ContactsData.ContactsDatabase()

    def handle_client(self, client_socket):
        """Обработка запросов клиента"""
        try:
            data = client_socket.recv(1024).decode("utf-8")

            if not data:
                return

            parts = data.split(";")

            if len(parts) < 1:
                print("[ERROR] Неверный формат данных:", data)
                client_socket.send("ERROR".encode("utf-8"))
                return

            command = parts[0]  # Первая часть — это команда
            params = parts[1:]  # Остальные части — параметры

            # Словарь с доступными командами
            commands = {
                "LOGIN": self.authorization_user,
                "REGISTER": self.register_user,
                "GET_TASKS": self.get_tasks,  # получение задач
                "ADD_TASK": self.add_task_db,  # добавление задачи
                "DELETE_TASKS_FROM_USER_ID": self.delete_tasks,
                "GET_USER_ID": self.get_user_id_db,
                "ADD_NOTE": self.add_note,
                "GET_NOTES": self.get_notes,
                "DELETE_NOTE": self.delete_note,
                "UPDATE_NOTE": self.update_note,
                "CHANGE_PASSWORD": self.change_password,
                "GET_STATS": self.get_stats,
                "ADD_CONTACT": self.add_contact,
                "GET_CONTACTS": self.get_contacts,
                "DELETE_CONTACT": self.delete_contact,
                "UPDATE_CONTACT": self.update_contact
            }

            # Проверяем, есть ли такая команда в списке
            if command in commands:
                commands[command](client_socket, *params)  # Вызываем нужную функцию с аргументами
            else:
                print(f"[ERROR] Неизвестная команда: {command}")
                client_socket.send("UNKNOWN_COMMAND".encode("utf-8"))

        except Exception as e:
            print(f"[ERROR] {e}")
            client_socket.send("FAIL".encode("utf-8"))

        finally:
            client_socket.close()

    def add_contact(self, client_socket, user_id, name, surname, phone, email):
        try:
            if self.db_contacts.create_or_update_contacts_table(user_id, name, surname, phone, email):
                client_socket.send(f"OK".encode("utf-8"))
        except Exception as e:
            print(f"[ERROR ADD_CONTACT] {e}")
            client_socket.send("ERROR".encode("utf-8"))
        finally:
            client_socket.close()

    def get_contacts(self, client_socket, user_id):
        try:
            contacts = self.db_contacts.get_contacts(user_id)
            result = "|".join([";".join(map(str, c)) for c in contacts])
            client_socket.send(result.encode("utf-8"))
        except Exception as e:
            print(f"[ERROR GET_CONTACTS] {e}")
            client_socket.send("NO_CONTACTS".encode("utf-8"))
        finally:
            client_socket.close()

    def delete_contact(self, client_socket, contact_id):
        try:
            if self.db_contacts.delete_contact(contact_id):
                client_socket.send("OK".encode("utf-8"))
            else:
                client_socket.send("FAIL".encode("utf-8"))
        except Exception as e:
            print(f"[ERROR DELETE_CONTACT] {e}")
            client_socket.send("ERROR".encode("utf-8"))
        finally:
            client_socket.close()

    def update_contact(self, client_socket, contact_id, name, surname, phone, email):
        try:
            self.db_contacts.update_contact(contact_id, name, surname, phone, email)
            client_socket.send("OK".encode("utf-8"))
        except Exception as e:
            print(f"[ERROR UPDATE_CONTACT] {e}")
            client_socket.send("ERROR".encode("utf-8"))
        finally:
            client_socket.close()

    def get_stats(self, client_socket, user_id):
        """Отправка статистики активности пользователя"""
        try:
            stats = self.db_user.get_user_stats(user_id)
            if stats:
                # Преобразуем словарь в строку формата: "tasks:12;notes:5;contacts:3"
                stats_str = ";".join([f"{key}:{value}" for key, value in stats.items()])
                client_socket.send(stats_str.encode("utf-8"))
                print(f"[STATS SENT] {stats_str}")
            else:
                client_socket.send("NO_DATA".encode("utf-8"))

        except Exception as e:
            print(f"[ERROR] Ошибка получения статистики: {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def change_password(self, client_socket, user_id, old_password, new_password):
        """Обработка смены пароля от клиента"""
        try:
            # Попытка смены пароля через модуль работы с пользователями
            if self.db_user.change_password(user_id, old_password, new_password):
                client_socket.send("SUCCESS".encode("utf-8"))
                print(f"[CHANGE PASSWORD] Пароль пользователя {user_id} изменён.")
            else:
                client_socket.send("INVALID_PASSWORD".encode("utf-8"))
                print(f"[CHANGE PASSWORD FAIL] Неверный старый пароль для пользователя {user_id}")

        except Exception as e:
            print(f"[ERROR] Ошибка при смене пароля: {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def delete_tasks(self, client_socket, user_id):
        try:
            if self.db_tasks.delete_tasks_from_user_id(user_id):
                client_socket.send("OK".encode("utf-8"))
                print(f"[DELETE SUCCESS] {user_id}")
            else:
                client_socket.send("FAIL".encode("utf-8"))
                print(f"[DELETE FAILED] {user_id}")

        except Exception as e:
            print(f"[ERROR] {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def add_note(self, client_socket, user_id, note_id, title, text):
        """Добавляет новую заметку"""
        try:
            self.db_notes.create_or_update_notes_table(user_id, note_id, title, text)
            client_socket.send("SUCCESS".encode("utf-8"))
            print(f"[ADD NOTE SUCCESS] {user_id}")

        except Exception as e:
            print(f"[ERROR] Ошибка добавления заметки: {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def delete_note(self, client_socket, note_id):
        """Удаляет заметку по ID"""
        try:
            self.db_notes.delete_user_note(note_id)
            client_socket.send("SUCCESS".encode("utf-8"))

        except Exception as e:
            print(f"[ERROR] Ошибка удаления заметки: {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def update_note(self, client_socket, note_id, new_title, new_text):
        """Обновляет заметку по ID"""
        try:
            self.db_notes.update_user_note(note_id, new_title, new_text)
            client_socket.send("SUCCESS".encode("utf-8"))

        except Exception as e:
            print(f"[ERROR] Ошибка обновления заметки: {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def get_notes(self, client_socket, user_id):
        """Получение заметок пользователя по его ID"""
        try:
            notes = self.db_notes.get_notes_from_db(user_id)

            if not notes:
                client_socket.send("NO_NOTES".encode("utf-8"))  # Если заметок нет
                return

            # Формируем строку для передачи
            notes_data = "\n".join([f"{note[0]}|{note[1]}|{note[2]}" for note in notes])
            client_socket.send(notes_data.encode("utf-8"))
            print(f"[GET NOTES SUCCESS] {user_id}")

        except Exception as e:
            print(f"[ERROR] Не удалось получить заметки: {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def get_tasks(self, client_socket, user_id):
        """Получение задач пользователя по его ID"""
        try:
            # Получаем задачи пользователя из базы данных
            tasks = self.db_tasks.get_user_tasks(user_id)

            if not tasks:
                client_socket.send("NO_TASKS".encode("utf-8"))  # Если задач нет
                return

            # Отправляем задачи пользователю
            task_data = "\n".join([f"{task[0]}|{task[1]}" for task in tasks])  # Формируем строку задач
            client_socket.send(task_data.encode("utf-8"))


        except Exception as e:
            print(f"[ERROR] Не удалось получить задачи: {e}")
            client_socket.send("ERROR".encode("utf-8"))
        finally:
            client_socket.close()

    def authorization_user(self, client_socket, username, password):
        """Авторизация пользователя"""
        try:
            print(f"[LOGIN ATTEMPT] {username}")

            # Проверяем пользователя в базе данных
            if self.db_user.check_user(username, password):
                client_socket.send("OK".encode("utf-8"))
                print(f"[LOGIN SUCCESS] {username}")
            else:
                client_socket.send("FAIL".encode("utf-8"))
                print(f"[LOGIN FAILED] {username}")

        except Exception as e:
            print(f"[ERROR] {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def register_user(self, client_socket, username, password):
        """Регистрация нового пользователя"""
        try:

            print(f"[LOGIN ATTEMPT] {username}")

            # Добавляем пользователя в базу данных
            if self.db_user.create_user_db(username, password):
                client_socket.send("OK".encode("utf-8"))
                print(f"[REGISTER SUCCESS] {username}")
            else:
                client_socket.send("FAIL".encode("utf-8"))
                print(f"[REGISTER FAILED] {username}")

        except Exception as e:
            print(f"[ERROR] {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def add_task_db(self, client_socket, username, task, status):
        try:
            if self.db_tasks.create_or_update_task_table(username, task, status):
                client_socket.send("OK".encode("utf-8"))
                print(f"[ADD TASK SUCCESS] {username}")
            else:
                client_socket.send("FAIL".encode("utf-8"))
                print(f"[ADD TASK FAILED]")

        except Exception as e:
            print(f"[ERROR] {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def get_user_id_db(self, client_socket, username):
        """Возвращает user_id по username"""
        try:
            if self.db_user.connect_db():
                self.user_id = self.db_user.get_user_id(username)

                if self.user_id:
                    client_socket.send(str(self.user_id[0]).encode("utf-8"))
                    print(f"[INFO] Найден user_id: {self.user_id[0]} для {username}")
                else:
                    client_socket.send("NOT_FOUND".encode("utf-8"))
                    print(f"[WARNING] Пользователь {username} не найден")

        except Exception as e:
            print(f"[ERROR] {e}")
            client_socket.send("ERROR".encode("utf-8"))

        finally:
            client_socket.close()

    def start(self):
        """Запуск сервера и обработка клиентов в потоках"""
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"[NEW CONNECTION] {addr}")

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()
