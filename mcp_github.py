import asyncio
import os
import json
import httpx
from dotenv import load_dotenv
from dedalus_labs import AsyncDedalus, DedalusRunner, AuthenticationError

load_dotenv()

# --- CONFIGURATION ---
# Replace with your actual repo: "username/repo-name"
TARGET_REPO = os.getenv("TARGET_REPO", "nishsm/sample-burnout-repo")
GITHUB_PER_PAGE = int(os.getenv("GITHUB_PER_PAGE", "15"))


async def fetch_commits_directly():
    """
    Fetch commits directly via the GitHub REST API using GITHUB_TOKEN.
    Returns a list of dicts: [{"message": ..., "author_name": ..., "date": ...}, ...]
    If no token is configured or an error occurs, returns an empty list.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        # No token configured; signal caller to fall back to MCP
        return []

    url = f"https://api.github.com/repos/{TARGET_REPO}/commits?per_page={GITHUB_PER_PAGE}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, headers=headers)
        except Exception as e:
            print(f"❌ GitHub direct fetch failed (network): {e}")
            return []

    if resp.status_code != 200:
        print(f"❌ GitHub direct fetch failed ({resp.status_code}): {resp.text}")
        return []

    try:
        raw = resp.json()
    except Exception as e:
        print(f"❌ Failed to parse GitHub response JSON: {e}")
        return []

    commits = []
    for item in raw:
        commit = item.get("commit", {})
        author = commit.get("author", {}) or {}
        author_name = author.get("name") or (item.get("author", {}) or {}).get("login") or "unknown"
        commits.append({
            "message": commit.get("message", ""),
            "author_name": author_name,
            "date": author.get("date") or ""
        })
    return commits


async def get_github_data_via_mcp():
    """
    First try direct GitHub API (reliable if GITHUB_TOKEN present).
    If that fails or returns empty, use the Dedalus MCP GitHub tool.
    Returns either a list of commit dicts or the raw MCP output.
    """
    # Try direct fetch first
    direct = await fetch_commits_directly()
    if direct:
        print("✅ Fetched commits directly from GitHub (GITHUB_TOKEN).")
        return direct

    api_key = os.getenv("DEDALUS_API_KEY")
    client = AsyncDedalus(
        api_key=api_key,
        base_url=os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai"),
        as_base_url=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
    )
    runner = DedalusRunner(client)

    print(f"\n🔌 CONNECTING TO MCP SERVER: issac/github-mcp...")
    print(f"🎯 TARGET: {TARGET_REPO}")

    prompt = f"""
    Use the GitHub tool to list the last {GITHUB_PER_PAGE} commits for the repository '{TARGET_REPO}'.

    Return the data as a pure JSON list with these fields only:
    - message
    - author_name
    - date
    """

    try:
        result = await runner.run(
            input=prompt,
            model=os.getenv("MCP_MODEL", "openai/gpt-4o"),
            mcp_servers=[os.getenv("GITHUB_MCP_SLUG", "issac/github-mcp")]
        )
        return result.output

    except AuthenticationError as e:
        # Handle OAuth connect_url flow (first-run)
        print("\n" + "="*60)
        print("⚠️  AUTHENTICATION REQUIRED FOR MCP")
        print("="*60)
        if hasattr(e, "body") and isinstance(e.body, dict):
            url = e.body.get("connect_url") or e.body.get("detail", {}).get("connect_url")
            if url:
                print(f"👉 Open this URL to authorize: {url}")
                input("\nPress ENTER after completing OAuth in the browser...")
                return await get_github_data_via_mcp()
        raise e


async def fetch_commits_via_mcp():
    """
    High-level wrapper that returns a list of commits as dicts:
    [{"message": ..., "author_name": ..., "date": ...}, ...]
    Attempts direct GitHub fetch first, then MCP if needed.
    """
    try:
        raw = await get_github_data_via_mcp()

        # If direct fetch returned structured list, return it
        if isinstance(raw, list):
            return raw

        # If MCP returned an object with .output-like shape
        if hasattr(raw, "output"):
            raw = raw.output

        # Try to parse JSON string returned by MCP
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass

        print("⚠️  Response could not be parsed as JSON/list. Raw output below:")
        print(raw)
        return []

    except Exception as e:
        print(f"❌ MCP/Error: {e}")
        return []


async def main():
    print("🚀 Fetching commits (direct then MCP fallback)...")
    commits = await fetch_commits_via_mcp()
    print("\n=== RESULT ===")
    try:
        print(json.dumps(commits, indent=2))
    except Exception:
        print(commits)


if __name__ == "__main__":
    asyncio.run(main())