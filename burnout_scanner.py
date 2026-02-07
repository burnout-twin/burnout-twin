import asyncio
import os
import json
import httpx
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
async def main():
    # Step 1: Fetch Data (Reliable Way)
    commits = await fetch_commits_directly()
    
    if not commits:
        return

    # Step 2: Analyze Data (AI Way)
    ai_response = await analyze_with_dedalus(commits)

    # Step 3: Print Results
    print("\n" + "="*40)
    print("🤖 DEDALUS DIAGNOSIS:")
    print("="*40)
    print(ai_response)

if __name__ == "__main__":
    asyncio.run(main())