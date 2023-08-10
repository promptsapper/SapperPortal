from .JsonSelfDifin import JsonFile


history_file = JsonFile('../forms/history.json')


def show_history_list(username, role):
    all_user_history = history_file.read_json()
    for user in all_user_history:
        if user["user"] == username and user["role"] == role:
            if not user["history"]:
                return {"history": "NULL"}
            else:
                return {"history": user["history"]}
    else:
        return {"history": "NULL"}


def find_single_history(username, role, history_id):
    history = history_file.read_json()
    for user in history:
        if user["user"] == username and user["role"] == role:
            for record in user["history"]:
                if record["history_id"] == history_id:
                    return {"single_history": record["content"]}


def single_history_delete(username, role, history_id):
    history = history_file.read_json()
    for user in history:
        if user["user"] == username and user["role"] == role:
            for record in user["history"]:
                if record["history_id"] == history_id:
                    user["history"].remove(record)
                    break
    history_file.write_json(history)