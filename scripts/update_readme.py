import os
import requests
from datetime import datetime, timezone
from dateutil import parser

GH_TOKEN = os.getenv("GH_TOKEN")
HEADERS = {"Authorization": f"token {GH_TOKEN}"} if GH_TOKEN else {}

README_PATH = "README.md"
REPO_OWNER = "dmitrij-el"
REPO_NAME = "dmitrij-el"


def fetch_last_commit(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    commit = r.json()[0]
    return {
        "message": commit["commit"]["message"].split("\n")[0],
        "url": commit["html_url"],
        "date": parser.parse(commit["commit"]["committer"]["date"])
    }


def fetch_latest_user_commit():
    url = f"https://api.github.com/users/{REPO_OWNER}/events/public"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    events = r.json()

    for event in events:
        if event["type"] == "PushEvent":
            repo = event["repo"]["name"]
            commit = event["payload"]["commits"][-1]
            return {
                "message": commit["message"].split("\n")[0],
                "url": f"https://github.com/{repo}/commit/{commit['sha']}",
                "repo": repo,
                "date": parser.parse(event["created_at"])
            }

    return None


def format_time(dt):
    now = datetime.now(timezone.utc)
    diff = now - dt
    if diff.days > 0:
        return f"{diff.days} дней назад"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} часов назад"
    minutes = diff.seconds // 60
    return f"{minutes} минут назад"


def update_readme(readme_path, data):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Формируем новый блок с коммитами
    commits_section = f"""
### 🚀 Последние коммиты

- **В этом репозитории:**  
  [`{data['self']['message']}`]({data['self']['url']}) — *{data['self']['time']}*  
- **В других репозиториях:**  
  [`{data['other']['message']}`]({data['other']['url']}) — *{data['other']['time']}*  
"""

    # Ищем место для вставки (например, после графика активности)
    insert_marker = "![GitHub Activity Graph](https://github-readme-activity-graph.vercel.app/graph?username=dmitrij-el&theme=radical)"
    if insert_marker in content:
        # Вставляем после графика активности
        new_content = content.replace(
            insert_marker,
            insert_marker + "\n\n" + commits_section
        )
    else:
        # Если маркер не найден, добавляем в конец
        new_content = content + "\n\n" + commits_section

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    self_commit = fetch_last_commit(REPO_OWNER, REPO_NAME)
    other_commit = fetch_latest_user_commit()

    data = {
        "self": {
            "message": self_commit["message"],
            "url": self_commit["url"],
            "time": format_time(self_commit["date"])
        },
        "other": {
            "message": other_commit["message"],
            "url": other_commit["url"],
            "time": format_time(other_commit["date"])
        } if other_commit else {
            "message": "нет данных",
            "url": "#",
            "time": "недоступно"
        }
    }

    update_readme(README_PATH, data)


if __name__ == "__main__":
    main()
