import os
import re
import urllib.request
import json

USERNAME = os.getenv("GITHUB_USERNAME", "AminodinAkbari")
README_PATH = "README.md"
MAX_EVENTS = 5


def fetch_recent_events(username: str) -> list[str]:
    url = f"https://api.github.com/users/{username}/events/public"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"{username}-profile-updater",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        events = json.loads(response.read().decode("utf-8"))

    lines: list[str] = []
    for event in events:
        event_type = event.get("type")
        repo_name = event.get("repo", {}).get("name", "")
        repo_url = f"https://github.com/{repo_name}"

        if event_type == "PushEvent":
            commits = len(event.get("payload", {}).get("commits", []))
            if commits > 0:
                lines.append(
                    f"- 🔨 Pushed **{commits}** commit(s) to [`{repo_name}`]({repo_url})"
                )
        elif event_type == "PullRequestEvent":
            action = event.get("payload", {}).get("action", "updated")
            pr = event.get("payload", {}).get("pull_request", {})
            pr_num = pr.get("number")
            pr_url = pr.get("html_url", repo_url)
            lines.append(
                f"- 🔀 {action.capitalize()} PR [#{pr_num}]({pr_url}) in [`{repo_name}`]({repo_url})"
            )
        elif event_type == "IssuesEvent":
            action = event.get("payload", {}).get("action", "updated")
            issue = event.get("payload", {}).get("issue", {})
            issue_num = issue.get("number")
            issue_url = issue.get("html_url", repo_url)
            lines.append(
                f"- 🐛 {action.capitalize()} issue [#{issue_num}]({issue_url}) in [`{repo_name}`]({repo_url})"
            )
        elif event_type == "CreateEvent":
            ref_type = event.get("payload", {}).get("ref_type", "repository")
            lines.append(
                f"- ✨ Created a new {ref_type} in [`{repo_name}`]({repo_url})"
            )

        if len(lines) >= MAX_EVENTS:
            break

    return lines


def update_readme(activity_lines: list[str]) -> None:
    if not activity_lines:
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    replacement = (
        "<!-- ACTIVITY:START -->\n"
        + "\n".join(activity_lines)
        + "\n<!-- ACTIVITY:END -->"
    )
    updated_content = re.sub(
        r"<!-- ACTIVITY:START -->.*?<!-- ACTIVITY:END -->",
        replacement,
        content,
        flags=re.DOTALL,
    )

    if updated_content != content:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(updated_content)


if __name__ == "__main__":
    recent = fetch_recent_events(USERNAME)
    update_readme(recent)
