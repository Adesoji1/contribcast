from langchain_openai import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv
import pandas as pd
import os
from datetime import date,datetime,timedelta,timezone
import requests
import schedule
import time
import base64
import random

load_dotenv()

@tool
def suggest_issues(username: str) -> str:
    """
    Suggest GitHub issues based on user's language and contributions.
    """
    import requests
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    query = f"""
    {{
      user(login: "{username}") {{
        repositories(first: 5, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
          nodes {{
            name
            languages(first: 3) {{
              nodes {{
                name
              }}
            }}
          }}
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    repos = response.json().get("data", {}).get("user", {}).get("repositories", {}).get("nodes", [])
    langs = [lang["name"] for repo in repos for lang in repo.get("languages", {}).get("nodes", [])]
    top_langs = list(set(langs))[:2] if langs else ["Python"]
    return f"Based on your repositories, contribute to issues in: {', '.join(top_langs)}.\nSee: https://github.com/issues?q=language:{top_langs[0]}+is:open+is:issue+is:good-first-issue"

def run_agent(username: str):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    system_prompt = (
        "You are a helpful assistant that analyzes GitHub activity. "
        "If the user asks for issue suggestions, use the `suggest_issues` tool."
    )

    prompt = f"The user wants to increase contributions. Should I suggest issues for GitHub user: {username}?"

    # Run tool directly
    result = suggest_issues.run(username)
    print(f"\n🤖 Suggestion:\n{result}\n")




def analyze_contribution_drop(contributions: dict) -> str:

    df = pd.DataFrame({
        "date": pd.to_datetime(list(contributions.keys())),
        "count": list(contributions.values())
    }).sort_values("date")

    recent = df.tail(14)
    this_week = recent.tail(7)["count"].sum()
    last_week = recent.head(7)["count"].sum()

    drop_pct = round((last_week - this_week) / last_week * 100, 1) if last_week else 0

    if drop_pct <= 0:
        return "✅ Your contributions are up or stable this week. Great job!"

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    prompt = (
        f"My GitHub contributions dropped by {drop_pct}% this week compared to last. "
        "Give me a motivational reflection, and ask if I want to set a reminder."
    )
    result = llm.invoke(prompt)
    return f"📉 Weekly Drop: {drop_pct}%\n\n{result}"


def plan_contribution_goal(current_total: int, target: int, contributions_by_day: dict) -> str:

    today = date.today()
    days_left = (date(today.year, 12, 31) - today).days
    needed = target - current_total
    daily_target = round(needed / days_left, 1) if days_left > 0 else 0

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    prompt = (
        f"I want to hit {target} GitHub contributions by the end of the year.\n"
        f"I currently have {current_total} contributions.\n"
        f"There are {days_left} days left.\n"
        f"What should my weekly and daily contribution goals be?\n"
        f"Also, suggest how I can stay consistent, and whether I should do 'good first issues'."
    )
    plan = llm.invoke(prompt)

    return (
        f"\n🎯 Goal Planning for {target} Contributions\n"
        f"➡️ Contributions so far: {current_total}\n"
        f"📆 Days left in year: {days_left}\n"
        f"📈 Needed per day: {daily_target}\n\n"
        f"🧠 Agent Suggestion:\n{plan.content}"
    )


def suggest_relevant_github_issues(
    language: str = "python",
    labels: list = ["good first issue", "help wanted", "bug"]
) -> str:
    """
    1) Query trending & fresh repos in the given language.
    2) Fetch up to 3 open issues (with your labels, falling back to no labels).
    3) Shuffle them for randomness.
    4) Build clickable links for Slack & CLI parsing.
    5) Ask the LLM to choose one and explain why.
    """

    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }

    # 1) Pick some repos to look in
    today = datetime.now(timezone.utc)
    since = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    query_urls = [
        f"https://api.github.com/search/repositories?"
        f"q=stars:>=3000+language:{language}&sort=stars&order=desc&per_page=5",
        f"https://api.github.com/search/repositories?"
        f"q=created:>={since}+forks:>=100+language:{language}"
        "&sort=stars&order=desc&per_page=5"
    ]

    repos = []
    for url in query_urls:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            repos.extend(resp.json().get("items", []))

    # 2) Collect up to 3 issues across those repos
    issues_found = []
    for repo in repos:
        if len(issues_found) >= 3:
            break

        owner = repo["owner"]["login"]
        name = repo["name"]
        issues_url = f"https://api.github.com/repos/{owner}/{name}/issues"

        # try with labels
        params = {"state": "open", "labels": ",".join(labels), "per_page": 3}
        r1 = requests.get(issues_url, headers=headers, params=params)
        items = []
        if r1.status_code == 200:
            items = [i for i in r1.json() if "pull_request" not in i]

        # fallback without labels
        if not items:
            r2 = requests.get(issues_url, headers=headers, params={"state": "open", "per_page": 3})
            if r2.status_code == 200:
                items = [i for i in r2.json() if "pull_request" not in i]

        for i in items:
            issues_found.append({
                "title": i["title"],
                "url":   i["html_url"],
                "repo":  f"{owner}/{name}"
            })
            if len(issues_found) >= 3:
                break

    if not issues_found:
        return "❌ No matching issues found right now. Try again later."

    # 3) Shuffle for randomness
    random.shuffle(issues_found)

    # 4) Build clickable link block (ctx)
    ctx = "\n\n".join(
        "• <https://github.com/{repo}|{repo}> – {title} (<{url}|view issue>)".format(
            repo=i["repo"], title=i["title"], url=i["url"]
        )
        for i in issues_found
    )

    # 5) Let the LLM pick one and explain
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    prompt = (
        f"I found these beginner-friendly open issues in {language} repositories:\n\n"
        f"{ctx}\n\n"
        "Which one should I start with, and why?"
    )
    suggestion = llm.invoke(prompt).content

    # 6) Return both the links (so CLI can auto‑PR) and the LLM’s suggestion
    return f"{ctx}\n\n🚀 Suggested GitHub Issues for {language}:\n\n{suggestion}"


def suggest_issues_by_domain(domain: str) -> str:
    domain_map = {
        "ai": {
            "language": "python",
            "labels": ["machine learning", "deep learning", "good first issue"]
        },
        "react": {
            "language": "javascript",
            "labels": ["react", "good first issue", "frontend"]
        },
        "devops": {
            "language": "go",
            "labels": ["devops", "ci", "good first issue"]
        },
        "web": {
            "language": "javascript",
            "labels": ["web", "good first issue"]
        },
        "data": {
            "language": "python",
            "labels": ["data", "data science", "good first issue",]
        },
        "java": {
            "language": "java",
            "labels": ["java", "good first issue","awaiting triage", "bug","dependencies","enhancement","help wanted", "invalid","question","wontfix"]
        },
        "ruby": {
            "language": "ruby",
            "labels": ["ruby", "good first issue"]
        },
        "php": {
            "language": "php",
            "labels": ["php", "good first issue"]
        },
        "csharp": {
            "language": "csharp",
            "labels": ["csharp", "good first issue"]
        },
        "rust": {
            "language": "rust",
            "labels": [ "rust", "good first issue",
    "-Cprefer-dynamic",
    "-Zbuild-std",
    "-Zcrate-attr",
    "-Zdebuginfo-compression",
    "-Zdump-mir",
    "-Zdwarf-version",
    "-Zfmt-debug",
    "-Zllvm-plugins",
    "-Zmetrics-dir",
    "-Znormalize-docs",
    "-Zpolymorphize",
    "-Zrandomize-layout",
    "-Zshare-generics",
    "-Zterminal-urls",
    "-Zthir-unsafeck",
    "-Ztrace-macros",
    "-Zvalidate-mir",
    "A-a11y",
    "A-ABI",
    "A-align",
    "A-allocators",
    "A-array",
    "A-associated-items",
    "A-ast",
    "A-async-await",
    "A-async-closures",
    "A-atomic",
    "A-attributes",
    "A-auto-traits",
    "A-autovectorization"
]
        },
    }

    config = domain_map.get(
        domain.lower(),
        {"language": "python", "labels": ["good first issue"]}
    )

    return suggest_relevant_github_issues(
        language=config["language"],
        labels=config["labels"]
    )

def schedule_daily_suggestions(send_function):
    """
    Schedule daily suggestions at 09:00 AM.
    """
    def job():
        message = suggest_issues_by_domain("ai")  # change domain as needed
        send_function(message)

    schedule.every().day.at("09:00").do(job)
    print("📆 Daily issue suggestions scheduled every day at 09:00 AM.")
    while True:
        schedule.run_pending()
        time.sleep(60)


def schedule_weekly_suggestions(send_function):
    

    def job():
        message = suggest_issues_by_domain("ai")  # change domain as needed
        send_function(message)

    schedule.every().monday.at("09:00").do(job)
    print("📆 Weekly issue suggestions scheduled every Monday at 09:00 AM.")
    while True:
        schedule.run_pending()
        time.sleep(60)


def enhance_profile_readme(repo_slug: str) -> str:
    """
    1) Fetch README.md and root files from the given repo (owner/repo).
    2) Auto-detect project type from root filenames.
    3) Ask the LLM to improve it, injecting correct install/run commands.
    4) Push a branch, update README.md, and open a PR.
    """
    owner, repo = repo_slug.split("/", 1)
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    # --- 1) Get default branch & current README.md ---
    graphql = {
      "query": f"""
        {{
          repository(owner: "{owner}", name: "{repo}") {{
            defaultBranchRef {{ name }}
            object(expression: "HEAD:README.md") {{
              ... on Blob {{ text }}
            }}
          }}
        }}
      """
    }
    resp = requests.post("https://api.github.com/graphql", json=graphql, headers=headers)
    data = resp.json()["data"]["repository"]
    default_branch = data["defaultBranchRef"]["name"]
    old_readme = data["object"]["text"] or ""

    # --- 2) List root files to detect project type ---
    contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents?ref={default_branch}"
    files = requests.get(contents_url, headers=headers).json()
    filenames = {item["name"] for item in files}

    # detect
    if "package.json" in filenames:
        lang = "Node.js"
        install_cmd = "npm install"
        run_cmd = "node app.js  # or npm start"
    elif "Cargo.toml" in filenames:
        lang = "Rust"
        install_cmd = "cargo build"
        run_cmd = "cargo run"
    elif "pyproject.toml" in filenames:
        lang = "Python (Poetry)"
        install_cmd = "poetry install"
        run_cmd = "poetry run python main.py"
    elif "requirements.txt" in filenames or "setup.py" in filenames:
        lang = "Python"
        install_cmd = "pip install -r requirements.txt"
        run_cmd = "python main.py"
    else:
        lang = "Unknown"
        install_cmd = "<install‑command here>"
        run_cmd = "<run‑command here>"

    # --- 3) Rewrite with LLM, giving it the language context ---
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    prompt = (
        f"This is a {lang} project. Use `{install_cmd}` to install dependencies "
        f"and `{run_cmd}` to run the app. Please:\n"
        "1. Improve the writing for clarity and impact.\n"
        "2. Inject appropriate Markdown badges (e.g., build status, top languages).\n"
        "3. Include a Usage section that shows install & run commands.\n"
        "4. Keep it under 200 lines.\n\n"
        f"Current README.md:\n\n{old_readme}\n\n"
        "Return ONLY the new README.md content."
    )
    updated = llm.invoke(prompt).content

    # --- 4a) Create a new branch ---
    branch = "ai-readme-enhancement"
    ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
    base_sha = requests.get(f"{ref_url}/heads/{default_branch}", headers=headers).json()["object"]["sha"]
    requests.post(ref_url, json={
        "ref": f"refs/heads/{branch}",
        "sha": base_sha
    }, headers=headers)

    # --- 4b) Commit updated README.md ---
    file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
    existing = requests.get(f"{file_url}?ref={default_branch}", headers=headers).json()
    payload = {
        "message": "chore: AI‑enhanced README",
        "content": base64.b64encode(updated.encode()).decode(),
        "branch": branch,
        "sha": existing["sha"]
    }
    requests.put(file_url, json=payload, headers=headers)

    # --- 4c) Open a PR ---
    pr = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        json={
            "title": "✨ AI‑enhanced README",
            "head": branch,
            "base": default_branch,
            "body": "Autogenerated by Contribcast’s README enhancer."
        },
        headers=headers
    ).json()

    return f"🚀 PR opened: {pr['html_url']}"


