import customtkinter as ctk
import re
from Client.Responses.tasks_responses import *


class TasksPage:
    def __init__(self, parent_frame, client, user_id):
        """Создаем менеджер задач внутри переданного родительского виджета"""
        self.parent_frame = parent_frame  # Родительский фрейм, в котором будет находиться UI задач
        self.client = client  # Клиент для взаимодействия с сервером
        self.user_id = user_id  # ID текущего пользователя

        self.tasks = []  # Список для хранения текстов задач
        self.task_entry_frame = None  # Фрейм для ввода задачи (создается при добавлении задачи)
        self.task_texts = {}  # Словарь для хранения оригинальных текстов задач {task_widget: text}
        self.task_status = {}  # Словарь для хранения статусов задач {task_widget: status}

    def create_tasks_page(self):
        """Создает и отображает страницу с задачами"""
        frame = ctk.CTkFrame(self.parent_frame)
        frame.pack(fill="both", expand=True)

        # Заголовок страницы
        self.tasks_list_label = ctk.CTkLabel(frame, text="Список задач", font=("Arial", 18))
        self.tasks_list_label.pack(pady=(10, 5))

        # Фрейм со списком задач (прокручиваемый)
        self.tasks_frame = ctk.CTkScrollableFrame(frame)
        self.tasks_frame.pack(fill="both", expand=True, pady=5, padx=5)

        # Фрейм для кнопок управления задачами
        self.button_tasks_frame = ctk.CTkFrame(frame)
        self.button_tasks_frame.pack(padx=5, pady=(10, 0))

        # Кнопка добавления новой задачи
        self.add_task_button = ctk.CTkButton(self.button_tasks_frame, text="Добавить задачу",
                                             command=self.show_task_entry)
        self.add_task_button.grid(row=0, column=0, pady=10, padx=15)

        # Кнопка сохранения всех задач в БД
        self.save_tasks_button = ctk.CTkButton(self.button_tasks_frame, text="Сохранить задачи",
                                               command=self.save_tasks_to_db)
        self.save_tasks_button.grid(row=0, column=1, pady=10, padx=15)

        # Метка для отображения ошибок или сообщений
        self.error_label = ctk.CTkLabel(frame, text="")
        self.error_label.pack()

        self.get_tasks_from_server()  # Загружаем задачи с сервера

        return frame

    def show_task_entry(self):
        """Отображает поле ввода для новой задачи"""
        if self.task_entry_frame is None:  # Проверяем, не создано ли уже поле ввода
            self.task_entry_frame = ctk.CTkFrame(self.tasks_frame)
            self.task_entry_frame.pack(fill="x", pady=5)

            # Поле ввода задачи с ограничением по символам
            self.task_entry = ctk.CTkEntry(self.task_entry_frame, width=400, placeholder_text="Введите задачу...",
                                           validate="key",
                                           validatecommand=(self.parent_frame.register(self.validate_input), '%P'))
            self.task_entry.pack(side="left", padx=5)

            # Кнопка подтверждения ввода
            confirm_button = ctk.CTkButton(self.task_entry_frame, text="✔", width=30, command=self.add_task)
            confirm_button.pack(side="right", padx=5)

    def save_tasks_to_db(self):
        """Сохраняет все задачи пользователя на сервере"""

        # Удаляем данные с сервера, чтобы их перезаписать
        if delete_tasks(self.client, self.user_id) == "OK":
            if not self.task_texts:  # проверяем словарь
                self.error_label.configure(text="Нет задач для сохранения!", text_color="red")
                return

        # Проверяем, совпадает ли количество задач и статусов
        if len(self.task_texts) != len(self.task_status):
            self.error_label.configure(text="Ошибка: несоответствие задач и статусов!", text_color="red")
            print("[ERROR] Количество задач и статусов не совпадает!")
            return

        for task_label, task_status_var in self.task_status.items():
            task_text = self.task_texts[task_label]  # Получаем текст задачи

            # Получаем текущий статус задачи
            task_status_text = task_status_var.get() if isinstance(task_status_var, ctk.StringVar) else task_status_var

            # Отправляем задачи на сервер
            if save_tasks(self.client, self.user_id, task_text, task_status_text) == "OK":
                self.error_label.configure(text="Все задачи успешно сохранены!", text_color="green")
            else:
                self.error_label.configure(text="Ошибка при сохранении некоторых задач!", text_color="red")

    def get_tasks_from_server(self):
        """Получает список задач с сервера и отображает их"""

        # Получение задач с сервера
        tasks = get_tasks(self.client, self.user_id)

        if tasks == "NO_TASKS":
            print("[INFO] У пользователя нет задач.")
        else:
            for task_info in tasks:
                if task_info.strip():  # Проверяем, что строка не пустая
                    task_parts = task_info.split("|")
                    if len(task_parts) == 2:  # Ожидаем формат "текст|статус"
                        task_text, task_status = task_parts
                        self.add_task_to_ui(task_text, task_status)  # Добавляем задачу в UI
                    else:
                        print(f"[ERROR] Неверный формат задачи: {task_info}")

    def add_task_to_ui(self, task_text, task_status):
        """Добавляет задачу в пользовательский интерфейс"""
        task_frame = ctk.CTkFrame(self.tasks_frame)
        task_frame.pack(fill="x", pady=5)

        # Метка с текстом задачи
        task_label = ctk.CTkLabel(task_frame, text=task_text, anchor="w", font=("Arial", 14, "normal"))
        task_label.pack(side="left", padx=5, fill="x", expand=True)

        # Сохраняем оригинальный текст в словаре для дальнейшего использования
        self.task_texts[task_label] = task_text
        self.tasks.append(task_text)  # Добавляем задачу в общий список задач

        # Кнопка удаления задачи
        delete_button = ctk.CTkButton(task_frame, text="❌", width=30,
                                      command=lambda: self.remove_task(task_frame, task_label, task_text))
        delete_button.pack(side="right", padx=5)

        # Кнопка редактирования задачи
        edit_button = ctk.CTkButton(task_frame, text="✏", width=30,
                                    command=lambda: self.edit_task(task_label, task_frame, edit_button,
                                                                   status_dropdown))
        edit_button.pack(side="right", padx=5)

        # Выпадающий список для выбора состояния задачи (статус)
        status_var = ctk.StringVar(value=task_status)
        self.update_task_status(task_label, status_var)  # Обновляем отображение задачи с её статусом
        status_options = ["Не выполнено", "В процессе", "Выполнено"]
        status_dropdown = ctk.CTkComboBox(task_frame, values=status_options, variable=status_var, state="readonly",
                                          command=lambda s: self.update_task_status(task_label, status_var))
        status_dropdown.pack(side="right", padx=5)

        # Добавляем состояние в словарь для дальнейшей обработки
        self.task_status[task_label] = status_var

    def validate_input(self, value):
        """Функция для ограничения количества символов (макс. 100 символов)"""
        return len(value) <= 100  # Ограничиваем ввод до 100 символов

    def add_task(self):
        """Добавление новой задачи"""
        task_text = self.task_entry.get().strip()  # Получаем текст задачи из поля ввода

        if task_text:
            task_frame = ctk.CTkFrame(self.tasks_frame)
            task_frame.pack(fill="x", pady=5)

            # Метка с текстом задачи
            task_label = ctk.CTkLabel(task_frame, text=task_text, anchor="w", font=("Arial", 14, "normal"))
            task_label.pack(side="left", padx=5, fill="x", expand=True)

            # Сохраняем оригинальный текст задачи в словарь
            self.task_texts[task_label] = task_text
            self.tasks.append(task_text)

            # Кнопка удаления задачи
            delete_button = ctk.CTkButton(task_frame, text="❌", width=30,
                                          command=lambda: self.remove_task(task_frame, task_label, task_text))
            delete_button.pack(side="right", padx=5)

            # Кнопка редактирования задачи
            edit_button = ctk.CTkButton(task_frame, text="✏", width=30,
                                        command=lambda: self.edit_task(task_label, task_frame, edit_button,
                                                                       status_dropdown))
            edit_button.pack(side="right", padx=5)

            # Выпадающий список для выбора состояния задачи
            status_var = ctk.StringVar(value="Добавь статус")  # По умолчанию "Добавь статус"
            status_options = ["Не выполнено", "В процессе", "Выполнено"]
            status_dropdown = ctk.CTkComboBox(task_frame, values=status_options, variable=status_var, state="readonly",
                                              command=lambda s: self.update_task_status(task_label, status_var))
            status_dropdown.pack(side="right", padx=5)

            # Добавляем состояние задачи в словарь
            self.task_status[task_label] = status_var

        # Удаляем поле ввода после добавления задачи
        if self.task_entry_frame:
            self.task_entry_frame.destroy()  # Убираем фрейм с полем ввода
            self.task_entry_frame = None

    def edit_task(self, task_label, task_frame, edit_button, status_dropdown):
        """Редактирование задачи"""
        task_text = task_label.cget("text")  # Получаем текущий текст задачи

        # Убираем возможный значок статуса из текста задачи
        clean_text = re.sub(r" [✅⏳❌]+$", "", task_text)

        # Создаём поле ввода для редактирования текста задачи
        edit_entry = ctk.CTkEntry(task_frame, width=400)
        edit_entry.insert(0, clean_text)  # Вставляем текущий текст задачи в поле ввода
        edit_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Ограничиваем количество символов в поле редактирования
        edit_entry.configure(validate="key", validatecommand=(self.parent_frame.register(self.validate_input), '%P'))

        # Кнопка подтверждения изменений
        self.confirm_button = ctk.CTkButton(task_frame, text="✔", width=30,
                                            command=lambda: self.confirm_edit_task(task_label, edit_entry, edit_button,
                                                                                   status_dropdown))
        self.confirm_button.pack(side="right", padx=5)

        # Скрываем старый текст задачи и кнопки редактирования
        task_label.pack_forget()
        edit_button.pack_forget()
        status_dropdown.pack_forget()

    def confirm_edit_task(self, task_label, edit_entry, edit_button, status_dropdown):
        """Сохранение отредактированной задачи"""
        new_text = edit_entry.get().strip()  # Получаем новый текст задачи

        if new_text:
            # Обновляем текст задачи в словаре
            self.task_texts[task_label] = new_text

            # Получаем текущий статус задачи
            current_status = status_dropdown.get()

            # Восстанавливаем символ статуса в текст задачи
            status_symbol = " ❌" if current_status == "Не выполнено" else \
                " ⏳" if current_status == "В процессе" else \
                    " ✅" if current_status == "Выполнено" else ""

            # Обновляем отображаемый текст задачи
            task_label.configure(text=new_text + status_symbol, font=("Arial", 14, "normal"))

        task_label.pack(side="left", padx=5, fill="x", expand=True)  # Возвращаем метку задачи
        edit_button.pack(side="right", padx=5)  # Возвращаем кнопку редактирования
        status_dropdown.pack(side="right", padx=5)  # Возвращаем выпадающий список с состоянием
        edit_entry.destroy()  # Убираем поле редактирования
        self.confirm_button.destroy()  # Убираем кнопку подтверждения

    def update_task_status(self, task_label, status_var):
        """Обновление состояния задачи (меняет отображение в зависимости от статуса)"""
        status = status_var.get()  # Получаем выбранный статус

        # Обновляем состояние задачи в словаре
        self.task_status[task_label] = status_var

        # Получаем оригинальный текст задачи
        task_text = self.task_texts.get(task_label, task_label.cget("text"))

        # Обновляем отображение задачи в зависимости от статуса
        if status == "Выполнено":
            task_label.configure(font=("Arial", 14, "normal"), text=task_text + " ✅", text_color="Green")
        elif status == "В процессе":
            task_label.configure(font=("Arial", 14, "normal"), text=task_text + " ⏳", text_color="Orange")
        elif status == "Не выполнено":
            task_label.configure(font=("Arial", 14, "normal"), text=task_text + " ❌", text_color="Red")

    def remove_task(self, task_frame, task_label, task_text):
        """Удаление задачи"""
        self.tasks.remove(task_text)  # Удаляем задачу из списка
        self.task_texts.pop(task_label, None)  # Удаляем текст задачи из словаря
        self.task_status.pop(task_label)  # Удаляем статус задачи из словаря
        task_frame.destroy()  # Удаляем фрейм с задачей из интерфейса

