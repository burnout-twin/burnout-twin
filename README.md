# 🔥 Burnout Twin (Dedalus Hackathon 2026)

**Burnout Twin** is an AI-powered "Health Monitor" for developers. It connects to your digital life—GitHub, Slack, and Calendar—to detect early signs of burnout before they become a crisis.

Using **Dedalus AI**, it analyzes behavioral patterns like "Zombie Commits" (3 AM coding), "Social Withdrawal" (curt Slack replies), and "Despair Keywords" to generate a real-time Burnout Score.

## 🚀 Features
* **GitHub Scanner:** Detects late-night commits, erratic coding patterns, and distress in commit messages.
* **Slack Sentiment Sensor:** Analyzes social battery depletion and tone shifts.
* **Dedalus Intelligence:** Uses the Dedalus `issac/github-mcp` and GPT-4o to diagnose stress levels.

---

## 🛠️ Setup & Installation

### 1. Clone the repo
```bash
git clone [https://github.com/burnout-twin/burnout-twin.git](https://github.com/burnout-twin/burnout-twin.git)
cd burnout-twin

2. Install dependencies

You need Python 3.9+ installed.
Bash

pip install dedalus-labs python-dotenv httpx

3. Configure Environment Variables (CRITICAL)

This project requires API keys to function. You must create a .env file in the root directory.

    Create the file:
    Bash

    touch .env

    Open .env and paste the following configuration:
    Code snippet

    # --- Dedalus AI Keys (Required for Intelligence) ---
    DEDALUS_API_KEY=your_dedalus_key_here
    DEDALUS_API_URL=[https://api.dedaluslabs.ai](https://api.dedaluslabs.ai)
    DEDALUS_AS_URL=[https://as.dedaluslabs.ai](https://as.dedaluslabs.ai)

    # --- GitHub Token (Required for Scanning) ---
    # Generate at: GitHub Settings > Developer Settings > Personal Access Tokens (Classic)
    # Scope needed: 'repo' (Full control of private repositories)
    GITHUB_TOKEN=ghp_your_github_token_here

🏃‍♂️ How to Run
1. Run the Code Burnout Scanner

Checks for "Zombie Commits" (1 AM - 5 AM) and "Despair" keywords in your git history.
Bash

python3 burnout_scanner.py

2. Run the Social Battery Sensor

Simulates a Slack conversation that degrades from polite to toxic to demonstrate social withdrawal detection.
Bash

python3 slack_burnout.py

🧠 How It Works

    Data Ingestion: We pull raw activity data from developer tools using httpx and simulated logs.

    Pattern Recognition: Python logic filters for high-risk signals (timestamps, keywords).

    AI Diagnosis: Dedalus AI acts as a clinical psychologist, reviewing the evidence to provide a "Burnout Score" (0-100) and actionable advice.

## 🧩 Running with Dedalus MCPs (Spotify / Calendar / GitHub)

To use the MCP servers instead of local/simulated data, set `USE_MCP=true` in your `.env` and provide a valid `DEDALUS_API_KEY`.

Example `.env` additions:

```
USE_MCP=true
DEDALUS_API_KEY=your_dedalus_api_key_here
```

Run the orchestrator (development):

```bash
# fallback mode (direct GitHub)
export USE_MCP=false
python3 orchestrator.py

# MCP mode (Dedalus MCPs)
export USE_MCP=true
export DEDALUS_API_KEY="your_key_here"
python3 orchestrator.py
```

Quick test: run a single iteration by starting the orchestrator and Ctrl-C after one cycle, or use the `--once` flag (works for manual testing):

```bash
python3 orchestrator.py --once
```

Notes:
- If an MCP requires OAuth, `mcp_github.py` will print a connect URL on first run; open it in a browser and authorize.
- Do not commit `.env` or API keys to source control.