import customtkinter as ctk
from CTkListbox import *
import uuid  # Для генерации уникальных ID


class NotePage:
    def __init__(self, parent_frame, client, user_id):
        """Создаем менеджер заметок внутри переданного родительского виджета"""
        self.parent_frame = parent_frame  # Родительский фрейм, в котором будет находиться интерфейс заметок
        self.client = client  # Клиент для связи с сервером
        self.user_id = user_id  # ID текущего пользователя
        self.notes = {}  # Хранит заметки в формате {note_id: (title, text)}
        self.note_ids = []  # Список ID заметок для корректного отображения и удаления

    def create_notes_page(self):
        """Создает страницу заметок"""
        frame = ctk.CTkFrame(self.parent_frame)
        frame.pack(fill="both", expand=True)

        # Список заметок (слева)
        self.notes_listbox = CTkListbox(frame, width=200, height=300)
        self.notes_listbox.pack(side="left", padx=10, pady=(10, 100), fill="y")
        self.notes_listbox.bind("<<ListboxSelect>>", self.load_note)  # Привязываем выбор элемента к загрузке заметки

        # === Правый фрейм (ввод данных и кнопки) ===
        right_frame = ctk.CTkFrame(frame)
        right_frame.pack(side="right", fill="both", expand=True, pady=10)

        # Поля для заголовка и текста заметки
        self.title_entry = ctk.CTkEntry(right_frame, width=300, placeholder_text="Введите заголовок")
        self.title_entry.pack(side="top", padx=10, pady=5, fill="x")

        self.textbox = ctk.CTkTextbox(right_frame, width=300, height=200)
        self.textbox.pack(side="top", padx=10, pady=5, fill="x")

        # === Кнопки (в отдельном подфрейме) ===
        buttons_frame = ctk.CTkFrame(right_frame)
        buttons_frame.pack(pady=10)

        # Кнопки управления заметками
        self.add_button = ctk.CTkButton(buttons_frame, text="➕ Добавить", command=self.add_note)
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.save_button = ctk.CTkButton(buttons_frame, text="💾 Сохранить", command=self.save_note)
        self.save_button.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = ctk.CTkButton(buttons_frame, text="🗑 Удалить", fg_color="red", command=self.delete_note)
        self.delete_button.grid(row=1, column=0, padx=5, pady=5)

        self.clear_button = ctk.CTkButton(buttons_frame, text="🧹 Очистить поля", command=self.clear_entries)
        self.clear_button.grid(row=1, column=1, padx=5, pady=5)

        self.get_notes_from_server()  # Загружаем существующие заметки с сервера

        return frame

    def get_notes_from_server(self):
        """Запрашивает заметки с сервера и добавляет их в интерфейс"""
        if self.client.connect():
            note_data = self.client.send_data(f"GET_NOTES;{self.user_id}")  # Отправляем запрос на сервер

            if note_data and note_data not in ["ERROR", "NO_NOTES"]:
                notes = note_data.split("\n")  # Разбиваем полученные данные на строки

                self.notes.clear()
                self.note_ids.clear()
                self.notes_listbox.delete(0, "end")  # Очищаем список перед загрузкой новых данных

                for note_info in notes:
                    if note_info.strip():  # Игнорируем пустые строки
                        note_parts = note_info.split("|")
                        if len(note_parts) == 3:  # Формат "note_id|title|text"
                            note_id, note_title, note_text = note_parts
                            self.notes[note_id] = (note_title, note_text)
                            self.note_ids.append(note_id)
                            self.notes_listbox.insert("end", note_title)  # Добавляем заголовок в список UI

                print(f"[INFO] Загружено {len(self.notes)} заметок.")
            else:
                print("[INFO] У пользователя нет заметок или произошла ошибка.")

    def add_note(self):
        """Добавляет новую заметку"""
        if self.client.connect():
            title = self.title_entry.get().strip()  # Получаем введенный заголовок
            text = self.textbox.get("1.0", "end").strip()  # Получаем текст заметки

            if title and text:  # Проверяем, что оба поля заполнены
                note_id = str(uuid.uuid4())  # Генерируем уникальный ID для новой заметки

                # Отправляем данные на сервер
                response = self.client.send_data(f"ADD_NOTE;{self.user_id};{note_id};{title};{text}")

                if response == "SUCCESS":
                    self.notes[note_id] = (title, text)  # Сохраняем заметку локально
                    self.note_ids.append(note_id)
                    self.notes_listbox.insert("end", title)  # Добавляем заголовок в список UI
                    self.title_entry.delete(0, "end")  # Очищаем поле заголовка
                    self.textbox.delete("1.0", "end")  # Очищаем текстовое поле
                else:
                    print("[ERROR] Не удалось добавить заметку")

    def load_note(self, event=None):
        """Загружает выбранную заметку"""
        selected_index = self.notes_listbox.curselection()  # Получаем индекс выбранного элемента

        if selected_index is not None:
            note_id = self.note_ids[selected_index]  # Получаем ID заметки по индексу
            title, text = self.notes[note_id]  # Загружаем данные заметки
            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, title)  # Вставляем заголовок в поле ввода
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", text)  # Вставляем текст заметки

    def delete_note(self):
        """Удаляет заметку из UI и с сервера"""
        if self.client.connect():
            selected_index = self.notes_listbox.curselection()  # Получаем индекс выбранной заметки

            if selected_index is not None:
                note_id = self.note_ids.pop(selected_index)  # Удаляем ID из списка

                response = self.client.send_data(f"DELETE_NOTE;{note_id}")  # Отправляем запрос на удаление

                if response == "SUCCESS":
                    del self.notes[note_id]  # Удаляем заметку из локального хранилища
                    self.notes_listbox.delete(selected_index)  # Удаляем из списка UI
                    self.textbox.delete("1.0", "end")  # Очищаем текстовое поле
                    self.title_entry.delete(0, "end")  # Очищаем поле заголовка
                else:
                    print("[ERROR] Ошибка удаления заметки")

    def save_note(self):
        """Обновляет текст и заголовок заметки"""
        if self.client.connect():
            selected_index = self.notes_listbox.curselection()  # Получаем индекс выбранной заметки

            if selected_index is not None:
                note_id = self.note_ids[selected_index]  # Получаем ID заметки
                new_title = self.title_entry.get().strip()  # Новый заголовок
                new_text = self.textbox.get("1.0", "end").strip()  # Новый текст

                if new_title and new_text:  # Проверяем, что оба поля заполнены
                    response = self.client.send_data(f"UPDATE_NOTE;{note_id};{new_title};{new_text}")

                    if response == "SUCCESS":
                        self.notes[note_id] = (new_title, new_text)  # Обновляем данные локально
                        self.update_notes_list()  # Обновляем список заметок в UI
                    else:
                        print("[ERROR] Ошибка обновления заметки")

    def update_notes_list(self):
        """Обновляет список заметок"""
        self.notes_listbox.delete(0, 'end')  # Очищаем текущий список в UI

        for note_id, (title, _) in self.notes.items():
            self.notes_listbox.insert('end', title)  # Добавляем все заголовки заново

    def clear_entries(self):
        self.title_entry.delete(0, "end")
        self.textbox.delete("1.0", "end")
