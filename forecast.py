import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime,timedelta,date
import json

def forecast_contributions(contributions_by_day: dict):
    today = date.today()
    current_day = today.timetuple().tm_yday
    total_so_far = sum(contributions_by_day.values())
    rate = total_so_far / current_day
    return int(rate * (366 if today.year % 4 == 0 else 365))

def plot_contributions(contributions_by_day: dict):
    sns.set_theme(style="whitegrid")
    dates = list(contributions_by_day.keys())
    values = list(contributions_by_day.values())

    plt.figure(figsize=(12, 6))
    sns.lineplot(x=dates, y=values)
    plt.xticks(rotation=45)
    plt.title("GitHub Daily Contributions")
    plt.xlabel("Date")
    plt.ylabel("Contributions")
    plt.tight_layout()
    plt.show()

def show_contribution_heatmap(contributions: dict,save=False):
   

    df = pd.DataFrame({
        "date": pd.to_datetime(list(contributions.keys())),
        "count": list(contributions.values())
    })
    df["day"] = df["date"].dt.dayofweek  # Monday = 0
    df["week"] = df["date"].dt.isocalendar().week

    pivot = df.pivot_table(index="day", columns="week", values="count", fill_value=0)

    plt.figure(figsize=(20, 4))
    sns.heatmap(pivot, cmap="Greens", linewidths=1, cbar=True)
    plt.title("GitHub Contribution Heatmap")
    plt.yticks(ticks=[0.5,1.5,2.5,3.5,4.5,5.5,6.5], labels=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], rotation=0)
    plt.xlabel("Week Number")
    plt.tight_layout()

    if save:
        plt.savefig("heatmap.png")
    else:
        plt.show()


def calculate_streaks(contributions: dict) -> tuple:
    from datetime import datetime, timedelta

    dates = sorted(pd.to_datetime(list(contributions.keys())))
    values = [contributions[d.strftime('%Y-%m-%d')] for d in dates]

    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    today = datetime.today().date()
    yesterday = today - timedelta(days=1)

    # track backwards from today
    for i in reversed(range(len(dates))):
        day = dates[i].date()
        if contributions.get(day.isoformat(), 0) > 0:
            temp_streak += 1
            if day == today or day == yesterday or (dates[i+1].date() - day).days == 1:
                current_streak = temp_streak
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 0

    longest_streak = max(longest_streak, temp_streak)
    return current_streak, longest_streak

def show_weekly_summary(contributions: dict):

    today = datetime.today().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    labels = [d.strftime('%a') for d in last_7_days]
    values = [contributions.get(d.isoformat(), 0) for d in last_7_days]

    plt.figure(figsize=(8, 4))
    plt.bar(labels, values, color="skyblue")
    plt.title("Weekly Contributions (Last 7 Days)")
    plt.ylabel("Contributions")
    plt.tight_layout()
    plt.show()


def compare_users(user1: str, user2: str):
    from contribcast.github_agent import get_contributions_by_day
    user1_data = get_contributions_by_day(user1)
    user2_data = get_contributions_by_day(user2)

    u1_total = sum(user1_data.values())
    u2_total = sum(user2_data.values())
    if u2_total == 0:
        print(f"\n⚠️  Warning: {user2} has no public contributions this year or their account is private.")
    u1_proj = forecast_contributions(user1_data)
    u2_proj = forecast_contributions(user2_data)

    u1_streak, u1_longest = calculate_streaks(user1_data)
    u2_streak, u2_longest = calculate_streaks(user2_data)

    print(f"\n📊 Comparing {user1} vs {user2}")
    print(f"\nTotal Contributions: {user1} = {u1_total} | {user2} = {u2_total}")
    print(f"Forecasted Yearly:  {user1} = {u1_proj} | {user2} = {u2_proj}")
    print(f"Current Streak:     {user1} = {u1_streak} days | {user2} = {u2_streak} days")
    print(f"Longest Streak:     {user1} = {u1_longest} days | {user2} = {u2_longest} days")

def export_contributions_to_csv(contributions: dict, username: str):
    df = pd.DataFrame({
        "date": list(contributions.keys()),
        "count": list(contributions.values())
    })
    filename = f"{username}_contributions.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Exported contributions to {filename}")

def export_contributions_to_json(contributions: dict, username: str):
 
    filename = f"{username}_contributions.json"
    with open(filename, 'w') as f:
        json.dump(contributions, f)
    print(f"✅ Exported contributions to {filename}")