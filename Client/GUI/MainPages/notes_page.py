import customtkinter as ctk
from CTkListbox import *
import uuid  # Для генерации уникальных ID
from Client.Responses.notes_responses import *


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

        self.save_button = ctk.CTkButton(buttons_frame, text="💾 Сохранить", command=self.update_note)
        self.save_button.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = ctk.CTkButton(buttons_frame, text="🗑 Удалить", fg_color="red", command=self.delete_note)
        self.delete_button.grid(row=1, column=0, padx=5, pady=5)

        self.clear_button = ctk.CTkButton(buttons_frame, text="🧹 Очистить поля", command=self.clear_entries)
        self.clear_button.grid(row=1, column=1, padx=5, pady=5)

        self.get_notes_from_server()  # Загружаем существующие заметки с сервера

        return frame

    def get_notes_from_server(self):
        """Запрашивает заметки с сервера и добавляет их в интерфейс"""

        notes = get_notes(self.client, self.user_id)
        if notes is None:
            return

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

    def add_note(self):
        """Добавляет новую заметку"""

        title = self.title_entry.get().strip()  # Получаем введенный заголовок
        text = self.textbox.get("1.0", "end").strip()  # Получаем текст заметки
        note_id = None

        if send_note(self.client, self.user_id, title, text, note_id) == "OK":
            self.notes[note_id] = (title, text)  # Сохраняем заметку локально
            self.note_ids.append(note_id)
            self.notes_listbox.insert("end", title)  # Добавляем заголовок в список UI
            self.title_entry.delete(0, "end")  # Очищаем поле заголовка
            self.textbox.delete("1.0", "end")  # Очищаем текстовое поле

        else:
            print("[ERROR] Не удалось добавить заметку")

    def delete_note(self):
        """Удаляет заметку из UI и с сервера"""

        if remove_note(self.client, self.notes_listbox, self.note_ids, self.notes) == "OK":
            self.textbox.delete("1.0", "end")  # Очищаем текстовое поле
            self.title_entry.delete(0, "end")  # Очищаем поле заголовка
        else:
            print("[ERROR] Ошибка удаления заметки")

    def update_note(self):
        """Обновляет текст и заголовок заметки"""

        new_title = self.title_entry.get().strip()  # Новый заголовок
        new_text = self.textbox.get("1.0", "end").strip()  # Новый текст

        if update_note_data(self.client, self.notes_listbox, self.note_ids, self.notes, new_title, new_text) == "OK":
            self.update_notes_list()  # Обновляем список заметок в UI
        else:
            print("[ERROR] Ошибка обновления заметки")

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

    def update_notes_list(self):
        """Обновляет список заметок"""

        self.notes_listbox.delete(0, 'end')  # Очищаем текущий список в UI

        for note_id, (title, _) in self.notes.items():
            self.notes_listbox.insert('end', title)  # Добавляем все заголовки заново

    def clear_entries(self):
        # Очистка всех полей ввода
        self.title_entry.delete(0, "end")
        self.textbox.delete("1.0", "end")
