import os
import requests
from datetime import datetime, timedelta

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}


def format_time(dt):
    now = datetime.now()
    diff = now - dt
    if diff.days > 0:
        return f"{diff.days} дней назад"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} часов назад"
    return "только что"


def get_last_activity():
    url = f"https://api.github.com/users/dmitrij-el/events/public"
    try:
        response = requests.get(url, headers=HEADERS)
        events = response.json()

        if not isinstance(events, list):
            return "Не удалось получить активность"

        last_event = events[0]
        repo_name = last_event['repo']['name']
        event_type = last_event['type']
        created_at = datetime.strptime(last_event['created_at'], '%Y-%m-%dT%H:%M:%SZ')

        if event_type == 'PushEvent':
            commit_msg = last_event['payload']['commits'][0]['message']
            return f"🔨 Pushed to [{repo_name}](https://github.com/{repo_name}): {commit_msg} ({format_time(created_at)})"
        elif event_type == 'PullRequestEvent':
            pr_action = last_event['payload']['action']
            return f"🔀 PR {pr_action} in [{repo_name}](https://github.com/{repo_name}) ({format_time(created_at)})"
        else:
            return f"⚡ Activity in [{repo_name}](https://github.com/{repo_name}): {event_type} ({format_time(created_at)})"

    except Exception as e:
        return f"⚠️ Ошибка при получении активности: {str(e)}"


def update_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content.replace(
        '<!-- Здесь будет динамический контент через GitHub Actions -->',
        get_last_activity()
    )

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(new_content)


if __name__ == "__main__":
    update