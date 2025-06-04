import requests
from datetime import datetime

GITHUB_API = "https://api.github.com"
USERNAME = "dmitrij-el"

def get_last_commit():
    url = f"{GITHUB_API}/users/{USERNAME}/events/public"
    response = requests.get(url).json()
    # Парсинг последнего события...
    return "Последнее обновление: " + datetime.now().strftime("%d.%m.%Y")

if __name__ == "__main__":
    with open("README.md", "r+") as f:
        content = f.read()
        updated = content.replace("<!-- DYNAMIC -->", get_last_commit())
        f.seek(0)
        f.write(updated)