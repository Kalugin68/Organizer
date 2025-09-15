from Client.User.password_hasher import PasswordHasher

def send_new_profile(client, username, password, correct_password):
    """Обработка регистрации пользователя"""

    # Проверка совпадения паролей
    if password == correct_password:

        if client.connect():
            # Хешируем пароль перед отправкой
            hashed_password = PasswordHasher.hash_password(password)
            # Отправляем данные на сервер
            response = client.send_data(f"REGISTER;{username};{hashed_password}")

            if response == "OK":
                return "OK"
            else:
                return "PROFILE EXISTS"
    else:
        return "INCORRECT PASSWORD"

    return None

def send_login(client, username, password):
    """Отправляет логин и пароль на сервер для авторизации"""

    if client.connect():
        # Отправляем данные на сервер
        response = client.send_data(f"LOGIN;{username};{password}")

        if response == "OK":
            return "OK"
        else:
            return "FAIL"

    return None

def get_user_id(client, username, user_id):
    """Запрашивает user_id у сервера по username"""

    if client.connect():
        response = client.send_data(f"GET_USER_ID;{username}")
        if response:
            user_id = response
            print(f"[INFO] Получен user_id: {user_id}")
        else:
            print("[ERROR] Не удалось получить user_id")
            user_id = None

    return user_id

def update_password(client, user_id, old_password, new_password, confirm_password):
    """Изменение пароля у профиля на сервере"""

    if client.connect():
        response = client.send_data(f"CHANGE_PASSWORD;{user_id};{old_password};{new_password}")

        if response == "SUCCESS":
            return "OK"
        elif response == "INVALID_PASSWORD":
            return "INVALID_PASSWORD"
        else:
            return "FAIL"

    return None

def get_stats(client, user_id):
    """Получение статистики пользователя с сервера"""

    if client.connect():
        try:
            response = client.send_data(f"GET_STATS;{user_id}")

            if response == "NO_DATA":
                return {"tasks": 0, "notes": 0, "contacts": 0}
            elif response == "ERROR":
                return {"tasks": "-", "notes": "-", "contacts": "-"}

            # Преобразуем строку вида tasks:12;notes:5;contacts:3
            parts = response.split(";")
            stats = {part.split(":")[0]: int(part.split(":")[1]) for part in parts}
            print(stats)
            return stats

        except Exception as e:
            print(f"[CLIENT] Ошибка загрузки статистики: {e}")
            return {"tasks": "-", "notes": "-", "contacts": "-"}

    return None