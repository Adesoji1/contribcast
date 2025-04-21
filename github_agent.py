import requests
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_contributions_by_day(username: str):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    today = datetime.date.today()
    current_year = today.year

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    from_date = f"{current_year}-01-01T00:00:00Z"
    to_date = today.isoformat() + "T23:59:59Z"

    variables = {
        "login": username,
        "from": from_date,
        "to": to_date,
    }

    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers
    )

    data = response.json()
    days = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    contributions = {}
    for week in days:
        for day in week["contributionDays"]:
            date = day["date"]
            count = day["contributionCount"]
            contributions[date] = count
    return contributions
