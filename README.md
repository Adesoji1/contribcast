
# 📈 Contribcast

**AI-powered GitHub contribution forecasting, issue suggestion, and productivity assistant — straight from your terminal.**

---

## 🚀 What is Contribcast?

`contribcast` is a Python CLI tool that helps developers:

- Forecast and visualize their GitHub contributions 📊  
- Get weekly reflection and motivational insights from AI 🧠  
- Discover trending beginner-friendly issues tailored to your stack 🔍  
- Automatically draft and submit PRs to practice contributing 💻  
- Schedule Slack reminders and generate dynamic README.md files 📝  
- Empower both beginner and advanced developers to stay consistent

Whether you're new to open source or a seasoned contributor, Contribcast keeps your contribution game strong, organized, and automated.

---

## 📦 Features at a Glance

| Category | Features |
|----------|----------|
| 📊 Analytics | `--forecast`, `--heatmap`, `--streak`, `--weekly-summary`, `--compare` |
| 🧠 Smart AI Insights | `--reflect`, `--goal`, `--suggest`, `--domain ai/react`, `--generate-readme` |
| 🔍 Issue Discovery | `--suggest-issue`, `--auto-pr`, `--domain`, `--schedule-weekly` |
| 🛠️ Productivity | `--export-csv`, `--export-json`, `--save-heatmap`, `--notify-user` |
| 🤖 Automation | Draft PRs to GitHub issues, generate README.md using AI |
| 💬 Team Tools | Slack DM fallback, weekly drops to your team’s Slack channel |

---

## ✅ Requirements

- **Python 3.11+**
- A GitHub personal access token with `repo` scope
- An OpenAI API key
- A Slack bot token (if using Slack integration)

---

## 🔐 Environment Variables

Before using Contribcast, create a `.env` file or export these in your terminal:

```bash
export GITHUB_TOKEN=ghp_your_token_here
export GITHUB_USERNAME=your_github_username
export OPENAI_API_KEY=sk-proj-7p0_STw-Dp
export SLACK_BOT_TOKEN=xoxb-your-slack-token
export SLACK_CHANNEL=#your-slack-channel
export WHATSAPP_TO=whatsapp:+234xxxxxxxxxx  # Optional
export TWILIO_SID=your_twilio_sid
export TWILIO_AUTH=your_twilio_auth_token
```

---

## 🔧 Installation

```bash
git clone https://github.com/adesoji1/contribcast.git
cd contribcast
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To run globally (optional):

```bash
pip install .
```

or

```bash
pip install contribcast
```
---

## 🧠 Examples

### Forecast Contributions
```bash
contribcast githubusername--forecast
```

### Visualize Your GitHub Heatmap
```bash
contribcast githubusername--heatmap
```

### Get Weekly Reflection from AI
```bash
contribcast githubusername--reflect --notify-user @adesoji
```

### Discover Trending Issues + Auto PR
```bash
contribcast githubusername--suggest-issue --auto-pr auto
```

### Generate README for Your Local Project
```bash
contribcast githubusername--generate-readme
```

### Compare Contributions between 2 different github ussers
```bash
contribcast adesoji1 --compare malcolmtomisin

👤 GitHub Username: adesoji1
📅 Contributions so far: 424


📊 Comparing adesoji1 vs malcolmtomisin

Total Contributions: adesoji1 = 424 | malcolmtomisin = 168
Forecasted Yearly:  adesoji1 = 1406 | malcolmtomisin = 557
Current Streak:     adesoji1 = 3 days | malcolmtomisin = 1 days
Longest Streak:     adesoji1 = 9 days | malcolmtomisin = 5 days  ,   
```



> Replace `adesoji1` and `malcolmtomisin` with your 2 different GitHub usernames.


### Other CLI Commands

```bash
contribcast githubusername --forecast
contribcast githubusername --heatmap
contribcast githubusername --save-heatmap
contribcast githubusername --weekly-summary
contribcast githubusername --streak
contribcast githubusername --compare someoneelse
contribcast githubusername --suggest

```

---

## 🧠 Why Contribcast?

### 🔥 For New Developers:
- Discover beginner-friendly issues in trending repos
- Automatically generate your first PRs with guidance
- Get motivational nudges to build consistency

### 💼 For Experienced Developers:
- Monitor contribution trends across your team
- Automate contribution goals with AI planning
- Save time with weekly Slack drops and batch automation

---

## 🗓️ Optional: Schedule Weekly Suggestions

Run once (e.g. with cron or `tmux`):

```bash
python3 contribcast/scheduler.py
```

This sends weekly issue suggestions to your Slack every Monday at 09:00 AM.

---

## 📚 See All CLI Commands

```bash
contribcast githubusername--commands
```

---

## 🧪 Testing Your Setup

To validate that everything works:

```bash
contribcast githubusername--forecast
contribcast githubusername--suggest-issue --auto-pr auto
contribcast githubusername--generate-readme
```

If these commands succeed, you're all set, don't forget to replace githubusernamewith your github username, !

---

## 🧠 Powered By

- 🧠 [LangChain](https://github.com/langchain-ai/langchain)
- 🔍 [GitHub REST & GraphQL APIs](https://docs.github.com/en/graphql)
- 💬 [OpenAI GPT-3.5-turbo](https://platform.openai.com/docs/models/gpt-3.5-turbo)
- 📡 [Twilio ](https://github.com/twilio/twilio-python)
- [Slack SDKs](https://tools.slack.dev/python-slack-sdk/)

---

## 💡 Future Roadmap

- Auto-plan contributions weekly
- Multi-user comparison dashboard
- GitHub Action integration
- Telegram notifications
- VSCode extension for inline usage

---

## Screenshot

Contribcast AutoPR
![help](/Screenshot/PRmadeingithub.png)

Contribcast Suggestion
![help](/Screenshot/agentsuggestion.png)

Contribcast Goal Suggestion
![help](/Screenshot/contribcast-goal.png)

---


## ✨ Author

Made with ❤️ by **Adesoji Alu**

> Feel free to contribute or fork. Keep contributing and cast your commit spells 🧙🏽‍♂️✨

---

## 📜 License

MIT License

```
Copyright (c) 2025 Adesoji Alu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


```

## ERRORS
You might be faced with `openai.RateLimitError: Error code: 429 ` , `slack or whatsapp token` error if you pass in the wrong credentials
