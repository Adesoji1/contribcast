import os
import click
import re

from contribcast.github_agent import get_contributions_by_day
from contribcast.forecast import (
    forecast_contributions,
    plot_contributions,
    show_contribution_heatmap,
    calculate_streaks,
    show_weekly_summary,
    compare_users,
    export_contributions_to_csv,
    export_contributions_to_json
)
from contribcast.github_llm_agent import (
    run_agent,
    analyze_contribution_drop,
    plan_contribution_goal,
    suggest_relevant_github_issues,
    suggest_issues_by_domain,
    schedule_daily_suggestions,
    schedule_weekly_suggestions,
    enhance_profile_readme
)
from contribcast.local_llm_agent import generate_local_readme
from contribcast.notifier import send_slack_message
from contribcast.github_auto_pr import auto_draft_pr

@click.command()
@click.pass_context
@click.option("--commands", "commands", is_flag=True,
              help="Show all available CLI options and exit")
@click.option("--forecast", "forecast", is_flag=True,
              help="Forecast yearly contributions")
@click.option("--suggest", "suggest", is_flag=True,
              help="Ask AI for suggestions")
@click.option("--heatmap", "heatmap", is_flag=True,
              help="Show GitHub-style heatmap")
@click.option("--save-heatmap", "save_heatmap", is_flag=True,
              help="Save heatmap to heatmap.png")
@click.option("--streak", "streak", is_flag=True,
              help="Show current and longest contribution streaks")
@click.option("--weekly-summary", "weekly_summary", is_flag=True,
              help="Show weekly summary of last 7 days")
@click.option("--compare", "compare", type=str,
              help="Compare forecast and streaks with another user")
@click.option("--export-csv", "export_csv", is_flag=True,
              help="Export contributions to CSV")
@click.option("--export-json", "export_json", is_flag=True,
              help="Export contributions to JSON")
@click.option("--reflect", "reflect", is_flag=True,
              help="Reflect on weekly contribution changes")
@click.option("--notify-user", "notify_user", type=str,
              help="Optional Slack @username for fallback DM")
@click.option("--goal", "goal", type=int,
              help="Set a yearly contribution goal (e.g., 2000)")
@click.option("--suggest-issue", "suggest_issue", is_flag=True,
              help="Find and suggest beginner-friendly GitHub issues")
@click.option("--domain", "domain", type=str,
              help="Filter issues by domain (e.g. ai, react)")
@click.option("--auto-pr", "auto_pr", type=str,
              help="Auto-open a draft PR to the given GitHub issue URL")
@click.option("--schedule-daily", "schedule_daily", is_flag=True,
              help="Run daily issue suggestions scheduler")
@click.option("--schedule-weekly", "schedule_weekly", is_flag=True,
              help="Run weekly issue suggestions scheduler")
@click.option("--enhance-readme", "enhance_readme", type=str,
              help="Owner/repo slug whose README to enhance via AI")
@click.option("--generate-readme", "generate_readme", is_flag=True,
              help="Generate or overwrite README.md based on local folder structure")
@click.argument("username")
def main(ctx,
         commands,
         forecast,
         suggest,
         heatmap,
         save_heatmap,
         streak,
         weekly_summary,
         compare,
         export_csv,
         export_json,
         reflect,
         notify_user,
         goal,
         suggest_issue,
         domain,
         auto_pr,
         schedule_daily,
         schedule_weekly,
         enhance_readme,
         generate_readme,
         username):
    """
    CLI tool to analyze GitHub contributions and more.
    """
    # Show help and exit
    if commands:
        click.echo(ctx.get_help())
        ctx.exit()

    # Daily scheduler
    if schedule_daily:
        click.echo("📆 Starting daily issue suggestion scheduler…")
        schedule_daily_suggestions(send_slack_message)
        return

    # Weekly scheduler
    if schedule_weekly:
        click.echo("📆 Starting weekly issue suggestion scheduler…")
        schedule_weekly_suggestions(send_slack_message)
        return

    # Generate local README
    if generate_readme:
        click.echo("📝 Generating README.md based on local folder structure…")
        generate_local_readme(os.getcwd())
        click.echo("✅ README.md created/updated.")
        return

    # Enhance remote README
    if enhance_readme:
        click.echo(f"📝 Enhancing README for '{enhance_readme}' via AI…")
        result = enhance_profile_readme(enhance_readme)
        click.echo(result)
        send_slack_message(result, fallback_user=notify_user)
        return

    # Contribution logic
    contributions = get_contributions_by_day(username)
    total = sum(contributions.values())
    click.echo(f"\n👤 GitHub Username: {username}")
    click.echo(f"📅 Contributions so far: {total}\n")

    if forecast:
        projected = forecast_contributions(contributions)
        click.echo(f"🔮 Estimated contributions for the year: {projected}")
        plot_contributions(contributions)

    if suggest:
        run_agent(username)

    if heatmap:
        show_contribution_heatmap(contributions)

    if save_heatmap:
        show_contribution_heatmap(contributions, save=True)
        click.echo("💾 Heatmap saved to heatmap.png")

    if streak:
        current, longest = calculate_streaks(contributions)
        click.echo(f"🔥 Current Streak: {current} days")
        click.echo(f"🏆 Longest Streak: {longest} days")

    if weekly_summary:
        show_weekly_summary(contributions)

    if compare:
        compare_users(username, compare)

    if export_csv:
        export_contributions_to_csv(contributions, username)
        click.echo(f"📊 Contributions exported to {username}_contributions.csv")

    if export_json:
        export_contributions_to_json(contributions, username)
        click.echo(f"📊 Contributions exported to {username}_contributions.json")

    if reflect:
        message = analyze_contribution_drop(contributions)
        click.echo(f"\n🧠 {message}\n")

    if goal:
        message = plan_contribution_goal(total, goal, contributions)
        click.echo(message)
        send_slack_message(message, fallback_user=notify_user)

    if suggest_issue:
        issue_suggestion = suggest_relevant_github_issues(language="python")
        click.echo(issue_suggestion)
        send_slack_message(issue_suggestion, fallback_user=notify_user)
        if auto_pr == "auto":
            if "❌" not in issue_suggestion:
                issue_urls = re.findall(r"https://github\.com/[^\s]+/issues/\d+", issue_suggestion)
                if issue_urls:
                    pr_url = auto_draft_pr(issue_urls[0])
                    click.echo(f"🚀 Draft PR opened: {pr_url}")
                else:
                    click.echo("⚠️ No valid issue URL found to create PR.")
            else:
                click.echo("⚠️ Cannot open draft PR because no issues were found.")
    
    if auto_pr and auto_pr != "auto":
        pr_url = auto_draft_pr(auto_pr)
        click.echo(f"🚀 Draft PR opened: {pr_url}")

    if domain:
        message = suggest_issues_by_domain(domain)
        click.echo(message)
        send_slack_message(message, fallback_user=notify_user)

if __name__ == "__main__":
    main()




