import asyncio
import os
import json
import webbrowser
import datetime
from typing import List, Dict, Any, TypeVar, Callable
from collections.abc import Awaitable
from dotenv import load_dotenv

load_dotenv()

from dedalus_labs import AsyncDedalus, AuthenticationError, DedalusRunner  # noqa: E402

class MissingEnvError(ValueError):
    """Required environment variable not set."""

def get_env(key: str) -> str:
    """Get required env var or raise."""
    val = os.getenv(key)
    if not val:
        raise MissingEnvError(f"Missing required env var: {key}")
    return val

API_URL = get_env("DEDALUS_API_URL")
AS_URL = get_env("DEDALUS_AS_URL")
DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY")  # Optional but recommended

# Debug: print env vars
print("=== Environment ===")
print(f"  DEDALUS_API_URL: {API_URL}")
print(f"  DEDALUS_AS_URL: {AS_URL}")
print(f"  DEDALUS_API_KEY: {DEDALUS_API_KEY[:20]}..." if DEDALUS_API_KEY else "  DEDALUS_API_KEY: None")

T = TypeVar("T")
RetryFn = Callable[[], Awaitable[T]]

async def with_oauth_retry(fn: RetryFn) -> T:
    """Run async function, handling OAuth browser flow if needed."""
    try:
        return await fn()
    except AuthenticationError as e:
        # Extract connect_url from error
        body = getattr(e, 'body', {}) if hasattr(e, 'body') else {}
        url = body.get("connect_url") or (body.get("detail", {}) if isinstance(body, dict) else {}).get("connect_url")
        if not url:
            raise
        print("\n" + "=" * 60)
        print("OAuth required. Opening browser for Gmail auth...")
        print(f"\nConnect URL: {url}")
        print("\nAfter auth, press Enter here...")
        print("=" * 60)
        webbrowser.open(url)
        input("Press Enter after completing OAuth in browser...")
        return await fn()

def normalize_email_stats(stats: Dict) -> Dict:
    """Normalize email count response."""
    return {
        "unread_count": stats.get("count", 0),
        "period": stats.get("period", ""),
        "query_used": stats.get("query", ""),
        **{k: v for k, v in stats.items() if k not in ["count", "period", "query"]}
    }

async def fetch_unread_email_count(days_back: int = 1) -> List[Dict]:
    """Check unread email count since N days ago via Gmail MCP."""
    mcp_servers = os.getenv("CALENDARMCP", "sintem/gmail-mcp").split(",")
    mcp_servers = [s.strip() for s in mcp_servers if s.strip()]

    client = AsyncDedalus(api_key=DEDALUS_API_KEY, base_url=API_URL, as_base_url=AS_URL)
    runner = DedalusRunner(client)

    # Calculate date since when to check (Gmail format: YYYY/MM/DD)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days_back)
    since_date = start_date.strftime("%Y/%m/%d")
    period = f"since {since_date} ({days_back} days ago)"

    prompt = f"""Use Gmail tools to count UNREAD emails {period}.
Search query: "is:unread since:{since_date}"
Return ONLY a JSON object like: {{"count": 42, "period": "{period}", "query": "is:unread since:{since_date}"}}.
If no tool available, estimate based on listing first 50 unread emails."""

    result = await with_oauth_retry(
        lambda: runner.run(
            input=prompt,
            model="openai/gpt-4o-mini",
            mcp_servers=mcp_servers,
        )
    )

    print("=== Model Output ===")
    print(result.output)

    # Parse output as JSON
    try:
        stats = json.loads(result.output)
        return [normalize_email_stats(stats)]
    except json.JSONDecodeError:
        print("Warning: Could not parse output as JSON.")
        import re
        match = re.search(r'\{.*\}', result.output, re.DOTALL)
        if match:
            try:
                stats = json.loads(match.group(0))
                return [normalize_email_stats(stats)]
            except json.JSONDecodeError:
                pass
    # Fallback: manual count if list returned
    try:
        emails = json.loads(result.output)
        if isinstance(emails, list):
            count = len([e for e in emails if e.get("unread", True)])
            return [{"count": count, "period": period, "query": f"is:unread since:{since_date}", "note": "Counted from list"}]
    except:
        pass
    print("Raw output used as fallback.")
    return [{"count": 0, "period": period, "error": "Could not parse response"}]

async def main() -> None:
    """Check unread emails."""
    print("=" * 60)
    print("Checking Unread Emails via Gmail MCP")
    print("=" * 60)
    days_back = int(os.getenv("DAYS_BACK", "1"))  # Set via env: DAYS_BACK=7
    try:
        stats = await fetch_unread_email_count(days_back)
        print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
