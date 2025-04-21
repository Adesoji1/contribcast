import schedule
import time
from contribcast.github_llm_agent import suggest_issues_by_domain
from contribcast.notifier import send_slack_message

def daily_job():
    msg = suggest_issues_by_domain("ai")
    send_slack_message(msg)

def weekly_job():
    msg = suggest_issues_by_domain("ai")
    send_slack_message(msg)

if __name__ == "__main__":
    # run daily at 09:00
    schedule.every().day.at("09:00").do(daily_job)
    # run weekly Mondays at 09:00
    schedule.every().monday.at("09:00").do(weekly_job)

    print("📆 Scheduler started: daily at 09:00 and weekly on Mondays at 09:00")
    while True:
        schedule.run_pending()
        time.sleep(60)
