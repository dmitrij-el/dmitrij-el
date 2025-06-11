import os
import requests
from datetime import datetime, timezone
from dateutil import parser

GH_TOKEN = os.getenv("GH_TOKEN")
HEADERS = {"Authorization": f"token {GH_TOKEN}"} if GH_TOKEN else {}

README_PATH = "README.md"
REPO_OWNER = "dmitrij-el"
REPO_NAME = "dmitrij-el"
COMMITS_SECTION_START = "<!-- COMMITS_SECTION_START -->"
COMMITS_SECTION_END = "<!-- COMMITS_SECTION_END -->"


def fetch_last_commit(owner, repo):
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        commit = r.json()[0]
        return {
            "message": commit["commit"]["message"].split("\n")[0],
            "url": commit["html_url"],
            "date": parser.parse(commit["commit"]["committer"]["date"])
        }
    except (requests.RequestException, IndexError, KeyError) as e:
        print(f"Error fetching last commit: {e}")
        return None


def fetch_latest_user_commit():
    try:
        url = f"https://api.github.com/users/{REPO_OWNER}/events/public"
        r = requests.get(url, headers=HEADERS, timeout=10)
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
    except (requests.RequestException, IndexError, KeyError) as e:
        print(f"Error fetching user events: {e}")
        return None


def format_time(dt):
    now = datetime.now(timezone.utc)
    diff = now - dt

    if diff.days > 0:
        days = diff.days
        return f"{days} {'день' if days == 1 else 'дня' if 2 <= days <= 4 else 'дней'} назад"

    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} {'час' if hours == 1 else 'часа' if 2 <= hours <= 4 else 'часов'} назад"

    minutes = diff.seconds // 60
    return f"{minutes} {'минуту' if minutes == 1 else 'минуты' if 2 <= minutes <= 4 else 'минут'} назад"


def update_readme(readme_path, data):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Формируем новый блок с коммитами
    commits_section = f"""{COMMITS_SECTION_START}
### 🚀 Последние коммиты

- **В этом репозитории:**  
  [`{data['self']['message']}`]({data['self']['url']}) — *{data['self']['time']}*  
- **В других репозиториях:**  
  [`{data['other']['message']}`]({data['other']['url']}) — *{data['other']['time']}*  
{COMMITS_SECTION_END}"""

    # Обновляем или добавляем секцию коммитов
    if COMMITS_SECTION_START in content and COMMITS_SECTION_END in content:
        # Заменяем существующую секцию
        start_idx = content.index(COMMITS_SECTION_START)
        end_idx = content.index(COMMITS_SECTION_END) + len(COMMITS_SECTION_END)
        new_content = content[:start_idx] + content[end_idx:]
    else:
        # Добавляем новую секцию после графика активности
        insert_marker = "![GitHub Activity Graph](https://github-readme-activity-graph.vercel.app/graph?username=dmitrij-el&theme=radical)"
        if insert_marker in content:
            new_content = content.replace(
                insert_marker,
                insert_marker + "\n\n" + commits_section
            )
        else:
            new_content = content + "\n\n" + commits_section

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    self_commit = fetch_last_commit(REPO_OWNER, REPO_NAME)
    other_commit = fetch_latest_user_commit()

    if not self_commit:
        print("Failed to fetch self commit, skipping update")
        return

    data = {
        "self": {
            "message": self_commit["message"],
            "url": self_commit["url"],
            "time": format_time(self_commit["date"])
        },
        "other": {
            "message": other_commit["message"] if other_commit else "нет данных",
            "url": other_commit["url"] if other_commit else "#",
            "time": format_time(other_commit["date"]) if other_commit else "недоступно"
        }
    }

    update_readme(README_PATH, data)


if __name__ == "__main__":
    main()