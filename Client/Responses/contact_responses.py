def get_contacts(client, user_id):
    # Подключаемся к клиенту и запрашиваем контакты пользователя
    if client.connect():
        response = client.send_data(f"GET_CONTACTS;{user_id}")
        if response and response not in ["ERROR", "NO_CONTACTS"]:
            contacts = response.split("|")  # Разделяем контакты по разделителю
            return contacts

    return None

def send_contact(client, user_id, name, surname, phone, email):
    # Добавляем новый контакт, если указаны имя и фамилия
    if client.connect():
        if name and surname:
            response = client.send_data(f"ADD_CONTACT;{user_id};{name};{surname};{phone};{email}")
            if response == "OK":
                return "OK"

    return None

def remove_contact(client, contacts_listbox, contact_ids, contacts):
    # Удаляем выбранный контакт из списка и сервера
    if client.connect():
        selected_index = contacts_listbox.curselection()
        if selected_index is not None:
            contact_id = contact_ids.pop(selected_index)
            response = client.send_data(f"DELETE_CONTACT;{contact_id}")
            if response == "OK":
                del contacts[contact_id]  # Удаляем из локального словаря
                contacts_listbox.delete(selected_index)  # Удаляем из UI
                return "OK"

    return None

def update_contact_data(client, contacts, contact_id, selected_index, name, surname, phone, email):
    # Обновляем данные контакта на сервере и локально
    if client.connect():
        if selected_index is not None:
            if name and surname:
                response = client.send_data(f"UPDATE_CONTACT;{contact_id};{name};{surname};{phone};{email}")
                if response == "OK":
                    contacts[contact_id] = (name, surname, phone, email)
                    return "OK"

    return None
