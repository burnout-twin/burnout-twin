import asyncio
import os
import json
import httpx
import signal
import sys
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from dedalus_labs import AsyncDedalus, DedalusRunner

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
TARGET_REPO = "nishsm/sample-burnout-repo" 

# --- 1. THE MANUAL FETCH (Bypasses MCP Auth Issues) ---
async def fetch_commits_directly():
    """
    Fetches commits using standard HTTP requests.
    Guaranteed to work if your GITHUB_TOKEN is valid.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ ERROR: GITHUB_TOKEN is missing from .env")
        return []

    print(f"📡 CONNECTING TO GITHUB (Direct API)... fetching {TARGET_REPO}")
    
    url = f"https://api.github.com/repos/{TARGET_REPO}/commits?per_page=15"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
    if response.status_code == 200:
        raw_data = response.json()
        # Clean the data for the AI (Send less tokens)
        clean_commits = []
        for item in raw_data:
            clean_commits.append({
                "message": item["commit"]["message"],
                "date": item["commit"]["author"]["date"]
            })
        return clean_commits
    elif response.status_code == 404:
        print(f"❌ Error 404: Repo '{TARGET_REPO}' not found. Check the name!")
    elif response.status_code == 401:
        print("❌ Error 401: Unauthorized. Your GITHUB_TOKEN is invalid.")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
    
    return []


def calculate_burnout_score_locally(commits):
    """
    Lightweight local heuristic to estimate burnout damage from commits.
    Returns a dict with 'damage' (int 0-100) and 'signals' (list).
    This mirrors the shape the orchestrator expects when deciding damage.
    """
    if not commits:
        return {"damage": 0, "signals": [], "count": 0}

    score = 0
    signals = []
    keywords = ["fix", "broken", "god", "wip", "urgent", "bug"]

    for c in commits:
        msg = (c.get("message") or "").lower()
        date_s = c.get("date") or c.get("author_date") or ""
        # Parse hour if possible
        try:
            dt = datetime.fromisoformat(date_s.replace("Z", "+00:00"))
            hour = dt.hour
        except Exception:
            hour = None

        # Zombie hours: 1-4 AM
        if hour is not None and 1 <= hour <= 4:
            score += 10
            signals.append(f"Zombie commit at hour {hour}")

        # Short/opaque messages
        if len(msg.strip()) > 0 and len(msg.strip()) < 5:
            score += 5
            signals.append("Short commit message")

        # Despair keywords
        for kw in keywords:
            if kw in msg:
                score += 8
                signals.append(f"Found keyword '{kw}' in message")
                break

    # Normalize and cap
    damage = min(100, score)

    return {"damage": damage, "signals": list(dict.fromkeys(signals)), "count": len(commits)}

# --- 2. THE DEDALUS BRAIN (Analysis) ---
async def analyze_with_dedalus(commits):
    """
    Uses Dedalus to analyze the JSON data we already fetched.
    """
    api_key = os.getenv("DEDALUS_API_KEY")
    client = AsyncDedalus(
        api_key=api_key,
        base_url=os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai"),
        as_base_url=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
    )
    runner = DedalusRunner(client)

    # We embed the data directly into the prompt
    prompt = f"""
    I am analyzing a developer's burnout levels. 
    Here is their recent commit history in JSON format:
    
    {json.dumps(commits, indent=2)}

    TASK:
    Analyze these commits for 3 signals:
    1. "Zombie Hours": Are timestamps between 1 AM and 5 AM?
    2. "Brain Fog": Are messages very short (under 5 chars) or vague?
    3. "Despair": Do they contain words like "fix", "broken", "god", "wip"?

    Return a JSON summary with:
    - "burnout_score" (0-100)
    - "signals" (list of strings describing what you found)
    """

    print("🧠 SENDING DATA TO DEDALUS AI...")
    
    # We don't need the MCP tool anymore because we provided the data!
    result = await runner.run(
        input=prompt,
        model="openai/gpt-4o"
    )
    
    return result.output

# --- 3. MAIN EXECUTION ---
async def run_worker(stop_event: asyncio.Event):
    """
    Worker that performs fetch + analysis. It respects `stop_event` and
    can be cancelled gracefully by the main runner.
    """
    # Step 1: Fetch Data (Reliable Way)
    if stop_event.is_set():
        print("⏹️  Stop requested before starting fetch.")
        return

    commits = await fetch_commits_directly()
    if stop_event.is_set():
        print("⏹️  Stop requested after fetch; aborting analysis.")
        return

    if not commits:
        return

    # Step 2: Analyze Data (AI Way)
    ai_response = await analyze_with_dedalus(commits)

    if stop_event.is_set():
        print("⏹️  Stop requested after analysis; skipping output.")
        return

    # Step 3: Print Results
    print("\n" + "="*40)
    print("🤖 DEDALUS DIAGNOSIS:")
    print("="*40)
    print(ai_response)


async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _set_stop():
        if not stop_event.is_set():
            print("\n⚠️  Stop signal received — shutting down gracefully...")
            stop_event.set()

    # Unix signal handlers (SIGINT / SIGTERM)
    try:
        loop.add_signal_handler(signal.SIGINT, _set_stop)
        loop.add_signal_handler(signal.SIGTERM, _set_stop)
    except NotImplementedError:
        # Some platforms (or event loops) may not support add_signal_handler
        signal.signal(signal.SIGINT, lambda *_: _set_stop())
        signal.signal(signal.SIGTERM, lambda *_: _set_stop())

    # Also allow users to press 'q' + Enter to quit (non-blocking)
    def _on_stdin():
        try:
            data = sys.stdin.readline()
        except Exception:
            data = None
        if data and data.strip().lower() in ("q", "quit", "exit"):
            _set_stop()

    try:
        loop.add_reader(sys.stdin.fileno(), _on_stdin)
    except Exception:
        # If adding reader isn't supported, ignore — signals still work.
        pass

    worker = asyncio.create_task(run_worker(stop_event))

    # Wait for either worker completion or stop_event
    done, pending = await asyncio.wait(
        [worker, asyncio.create_task(stop_event.wait())],
        return_when=asyncio.FIRST_COMPLETED,
    )

    # If stop was requested and worker is still running, cancel it.
    if stop_event.is_set() and not worker.done():
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            print("✅ Worker cancelled.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Fallback: ensure we exit gracefully on Ctrl-C
        print("\nKeyboardInterrupt: exiting.")