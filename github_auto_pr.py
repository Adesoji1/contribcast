import requests
import os
import base64
from urllib.parse import urlparse

def auto_draft_pr(issue_url: str, branch_name: str = "contribcast-draft"):
    github_token = os.getenv("GITHUB_TOKEN")
    github_username = os.getenv("GITHUB_USERNAME")
    if not github_token or not github_username:
        raise EnvironmentError("GITHUB_TOKEN and GITHUB_USERNAME must be set in .env")

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }

    # Parse issue URL like: https://github.com/owner/repo/issues/123
    parts = urlparse(issue_url)
    path_segments = parts.path.strip("/").split("/")
    if len(path_segments) < 4:
        raise ValueError("Invalid GitHub issue URL")

    owner, repo, _, issue_number = path_segments[:4]

    # Step 1: Fork the repository
    fork_url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    fork_resp = requests.post(fork_url, headers=headers)
    if fork_resp.status_code not in [200, 202]:
        raise Exception(f"Fork failed: {fork_resp.status_code} {fork_resp.text}")

    print(f"✅ Forked {owner}/{repo} to {github_username}/{repo}")

    # Step 2: Get default branch
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_resp = requests.get(repo_url, headers=headers)
    default_branch = repo_resp.json().get("default_branch", "main")

    # Step 3: Get the latest commit SHA from the default branch
    branch_url = f"https://api.github.com/repos/{github_username}/{repo}/git/ref/heads/{default_branch}"
    head_resp = requests.get(branch_url, headers=headers)
    if head_resp.status_code != 200:
        raise Exception("Failed to fetch default branch ref")
    base_sha = head_resp.json()["object"]["sha"]

    # Step 4: Create a new branch
    ref_url = f"https://api.github.com/repos/{github_username}/{repo}/git/refs"
    ref_data = {
        "ref": f"refs/heads/{branch_name}",
        "sha": base_sha
    }
    ref_resp = requests.post(ref_url, json=ref_data, headers=headers)
    if ref_resp.status_code != 201:
        raise Exception("Failed to create new branch")
    print(f"✅ Created new branch: {branch_name}")

    # Step 5: Create a file draft.md in the new branch
    content = base64.b64encode(f"This is a draft PR for issue #{issue_number}.\n\nExploring the issue...".encode()).decode()
    file_url = f"https://api.github.com/repos/{github_username}/{repo}/contents/draft.md"
    file_data = {
        "message": "Initial draft.md from contribcast agent",
        "content": content,
        "branch": branch_name
    }
    file_resp = requests.put(file_url, json=file_data, headers=headers)
    if file_resp.status_code != 201:
        raise Exception("Failed to create draft.md")
    print("✅ Created draft.md in new branch")

    # Step 6: Create a pull request
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    pr_data = {
        "title": "Exploring this issue for practice — draft by contribcast",
        "head": f"{github_username}:{branch_name}",
        "base": default_branch,
        "body": f"Auto-created draft PR for issue #{issue_number}\n\nThis is a practice pull request by contribcast."
    }
    pr_resp = requests.post(pr_url, json=pr_data, headers=headers)
    if pr_resp.status_code not in [200, 201]:
        raise Exception(f"Failed to open draft PR: {pr_resp.status_code} {pr_resp.text}")

    pr_link = pr_resp.json().get("html_url")
    print(f"🚀 Draft PR created: {pr_link}")
    return pr_link