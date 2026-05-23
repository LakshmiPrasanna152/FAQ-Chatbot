import json
import os
import time

HISTORY_FILE = "chat_history.json"


def load_all():

    if not os.path.exists(HISTORY_FILE):
        return {}

    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_all(data):

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def save(email, sid, messages, domain, title):

    data = load_all()

    if email not in data:
        data[email] = {}

    data[email][sid] = {
        "messages": messages,
        "domain": domain,
        "title": title,
        "ts": time.time()
    }

    save_all(data)


def load(email):

    data = load_all()

    return data.get(email, {})