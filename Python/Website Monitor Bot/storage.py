import json, os
from config import STORAGE_FILE

DEFAULT = {
    "sites": {},  # url -> { name, keyword, status, last_seen, response_time, added_by }
    "paused": False
}


def load() -> dict:
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    return dict(DEFAULT)


def save(data: dict):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_sites() -> dict:
    return load().get("sites", {})


def add_site(url: str, name: str, keyword: str = None):
    data = load()
    data["sites"][url] = {
        "name": name,
        "keyword": keyword,
        "status": "unknown",
        "last_checked": None,
        "response_time": None,
        "failures": 0
    }
    save(data)

def remove_site(url: str) -> dict:
    data = load()
    if url in data["sites"]:
        del data["sites"][url]
        save(data)
        return True
    return False

def update_site(url: str, **kwargs):
    data = load()
    if url in data["sites"]:
        data["sites"][url].update(kwargs)
        save(data)

def is_paused() -> bool:
    return load().get("paused", False)


def set_paused(val: bool):
    data = load()
    data["paused"] = val
    save(data)