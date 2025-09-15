import customtkinter as ctk
from CTkListbox import *
from Client.Responses.contact_responses import *


class ContactPage:
    def __init__(self, parent_frame, client, user_id):
        self.parent_frame = parent_frame
        self.client = client
        self.user_id = user_id
        self.contacts = {}  # {contact_id: (name, surname, phone, email)}
        self.contact_ids = []

    def create_contacts_page(self):
        # Основной фрейм страницы контактов
        frame = ctk.CTkFrame(self.parent_frame)
        frame.pack(fill="both", expand=True)

        # Список контактов слева
        self.contacts_listbox = CTkListbox(frame, width=200, height=300)
        self.contacts_listbox.pack(side="left", padx=10, pady=(10, 100), fill="y")
        self.contacts_listbox.bind("<<ListboxSelect>>", self.load_contact)

        # === Правый фрейм: поля ввода и кнопки ===
        right_frame = ctk.CTkFrame(frame)
        right_frame.pack(side="right", fill="both", expand=True, pady=10)

        # Поля ввода информации о контакте
        self.name_entry = ctk.CTkEntry(right_frame, width=300, placeholder_text="Имя")
        self.name_entry.pack(padx=10, pady=5, fill="x")
        self.surname_entry = ctk.CTkEntry(right_frame, width=300, placeholder_text="Фамилия")
        self.surname_entry.pack(padx=10, pady=5, fill="x")
        self.phone_entry = ctk.CTkEntry(right_frame, width=300, placeholder_text="Телефон")
        self.phone_entry.pack(padx=10, pady=5, fill="x")
        self.email_entry = ctk.CTkEntry(right_frame, width=300, placeholder_text="Email")
        self.email_entry.pack(padx=10, pady=5, fill="x")

        # Кнопки управления контактами
        buttons_frame = ctk.CTkFrame(right_frame)
        buttons_frame.pack(pady=10)

        self.add_button = ctk.CTkButton(buttons_frame, text="➕ Добавить", command=self.add_contact)
        self.add_button.grid(row=0, column=0, padx=5, pady=5)
        self.save_button = ctk.CTkButton(buttons_frame, text="💾 Сохранить", command=self.update_contact)
        self.save_button.grid(row=0, column=1, padx=5, pady=5)
        self.delete_button = ctk.CTkButton(buttons_frame, text="🗑 Удалить", fg_color="red", command=self.delete_contact)
        self.delete_button.grid(row=1, column=0, padx=5, pady=5)
        self.clear_button = ctk.CTkButton(buttons_frame, text="🧹 Очистить поля", command=self.clear_entries)
        self.clear_button.grid(row=1, column=1, padx=5, pady=5)

        # Загружаем контакты с сервера при инициализации
        self.get_contacts_from_server()

        return frame

    def get_contacts_from_server(self):
        # Получение списка контактов с сервера
        contacts = get_contacts(self.client, self.user_id)
        if contacts is None:
            return

        self.contacts.clear()
        self.contact_ids.clear()
        self.contacts_listbox.delete(0, "end")

        for contact_info in contacts:
            if contact_info.strip():
                contact_parts = contact_info.split(";")
                if len(contact_parts) == 5:
                    contact_id, name, surname, phone, email = contact_parts
                    self.contacts[contact_id] = (name, surname, phone, email)
                    self.contact_ids.append(contact_id)
                    self.contacts_listbox.insert("end", f"{name} {surname}")
        print(f"[INFO] Загружено {len(self.contacts)} контактов.")

    def add_contact(self):
        # Добавление нового контакта через сервер
        if send_contact(self.client, self.user_id, name=self.name_entry.get(), surname=self.surname_entry.get(),
                        phone=self.phone_entry.get(), email=self.email_entry.get()) == "OK":
            self.get_contacts_from_server()
            self.clear_entries()
        else:
            print("[ERROR] Не удалось добавить контакт")

    def delete_contact(self):
        # Удаление выбранного контакта
        if remove_contact(self.client, self.contacts_listbox, self.contact_ids, self.contacts) == "OK":
            self.clear_entries()
        else:
            print("[ERROR] Ошибка удаления контакта")

    def update_contact(self):
        # Обновление данных выбранного контакта
        selected_index = self.contacts_listbox.curselection()

        if update_contact_data(self.client, self.contacts, self.contact_ids[selected_index],
                               selected_index, self.name_entry.get().strip(), self.surname_entry.get().strip(),
                               self.phone_entry.get().strip(), self.email_entry.get().strip()) == "OK":
            self.update_contacts_list()

    def load_contact(self, event=None):
        # Загружаем выбранный контакт в поля ввода
        selected_index = self.contacts_listbox.curselection()
        if selected_index is not None:
            contact_id = self.contact_ids[selected_index]
            name, surname, phone, email = self.contacts[contact_id]
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, name)
            self.surname_entry.delete(0, "end")
            self.surname_entry.insert(0, surname)
            self.phone_entry.delete(0, "end")
            self.phone_entry.insert(0, phone)
            self.email_entry.delete(0, "end")
            self.email_entry.insert(0, email)

    def update_contacts_list(self):
        # Обновляем отображение списка контактов
        self.contacts_listbox.delete(0, 'end')
        for contact_id, (name, surname, _, _) in self.contacts.items():
            self.contacts_listbox.insert("end", f"{name} {surname}")

    def clear_entries(self):
        # Очищаем все поля ввода
        self.name_entry.delete(0, "end")
        self.surname_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
