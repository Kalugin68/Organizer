def save_tasks(client, user_id, task_text, task_status_text):
    """Сохраняет все задачи пользователя на сервере"""

    if client.connect():
        print(f"[INFO] Отправка задачи: '{task_text}', статус: '{task_status_text}'")

        # Отправляем данные на сервер
        response = client.send_data(f"ADD_TASK;{user_id};{task_text};{task_status_text}")

        if response == "OK":
            return "OK"
        else:
            return "ERROR"

    return None

def delete_tasks(client, user_id):
    """Удаляет все задачи на сервере для их перезаписи"""

    if client.connect():
        # Удаляем все задачи пользователя перед сохранением новых
        response = client.send_data(f"DELETE_TASKS_FROM_USER_ID;{user_id}")

        if response == "OK":
            return "OK"

    return None

def get_tasks(client, user_id):
    """Получает список задач с сервера"""

    if client.connect():
        # Отправляем запрос на сервер
        task_data = client.send_data(f"GET_TASKS;{user_id}")

        if task_data != "ERROR" and task_data != "NO_TASKS":
            tasks = task_data.split("\n")  # Разделяем список задач
            return tasks
        elif task_data == "NO_TASKS":
            return "NO_TASKS"

    return None