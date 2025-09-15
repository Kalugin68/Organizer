import uuid  # Для генерации уникальных ID

def get_notes(client, user_id):
    # Получаем список заметок пользователя с сервера
    if client.connect():
        response = client.send_data(f"GET_NOTES;{user_id}")
        if response and response not in ["ERROR", "NO_NOTES"]:
            notes = response.split("\n")  # Разделяем заметки по строкам
            return notes
    return None

def send_note(client, user_id, title, text, note_id):
    # Добавляем новую заметку
    if client.connect():
        if title and text:
            note_id = str(uuid.uuid4())  # Генерируем уникальный ID заметки
            response = client.send_data(f"ADD_NOTE;{user_id};{note_id};{title};{text}")
            if response == "SUCCESS":
                return "OK"
    return None

def remove_note(client, notes_listbox, note_ids, notes):
    # Удаляем выбранную заметку
    if client.connect():
        selected_index = notes_listbox.curselection()
        if selected_index is not None:
            note_id = note_ids.pop(selected_index)  # Убираем ID из списка
            response = client.send_data(f"DELETE_NOTE;{note_id}")
            if response == "SUCCESS":
                del notes[note_id]  # Удаляем локально
                notes_listbox.delete(selected_index)  # Удаляем из UI
                return "OK"
    return None

def update_note_data(client, notes_listbox, note_ids, notes, new_title, new_text):
    # Обновляем выбранную заметку
    if client.connect():
        selected_index = notes_listbox.curselection()
        if selected_index is not None:
            note_id = note_ids[selected_index]
            if new_title and new_text:
                response = client.send_data(f"UPDATE_NOTE;{note_id};{new_title};{new_text}")
                if response == "SUCCESS":
                    notes[note_id] = (new_title, new_text)  # Обновляем локально
                    return "OK"
    return None
