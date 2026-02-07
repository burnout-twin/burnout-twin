import asyncio
import os
import json
from dotenv import load_dotenv
from dedalus_labs import AsyncDedalus, DedalusRunner, AuthenticationError

load_dotenv()

# --- CONFIGURATION ---
# Replace with your actual repo: "username/repo-name"
TARGET_REPO = "nishsm/sample-burnout-repo" 

async def get_github_data_via_mcp():
    api_key = os.getenv("DEDALUS_API_KEY")
    client = AsyncDedalus(
        api_key=api_key,
        base_url=os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai"),
        as_base_url=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
    )
    runner = DedalusRunner(client)

    print(f"\n🔌 CONNECTING TO MCP SERVER: issac/github-mcp...")
    print(f"🎯 TARGET: {TARGET_REPO}")

    # The Prompt: We explicitly tell the AI to use the tool
    prompt = f"""
    Use the GitHub tool to list the last 5 commits for the repository '{TARGET_REPO}'.
    
    Return the data as a pure JSON list with these fields only:
    - message
    - author_name
    - date
    """

    try:
        # We specify the MCP server here
        result = await runner.run(
            input=prompt,
            model="openai/gpt-4o",
            mcp_servers=["issac/github-mcp"] # <--- THIS IS THE MAGIC LINE
        )
        
        return result.output

    except AuthenticationError as e:
        # This block handles the OAuth flow (First run only)
        print("\n" + "="*60)
        print("⚠️  AUTHENTICATION REQUIRED")
        print("="*60)
        # The error body usually contains the connect URL
        if hasattr(e, 'body') and isinstance(e.body, dict):
            url = e.body.get("connect_url") or e.body.get("detail", {}).get("connect_url")
            if url:
                print(f"👉 Click this link to authorize GitHub: {url}")
                input("\nPress ENTER after you have authorized in the browser...")
                # Retry recursively
                return await get_github_data_via_mcp()
        raise e

async def main():
    print("🚀 LAUNCHING MCP CONNECTION...")
    
    try:
        data = await get_github_data_via_mcp()
        
        print("\n✅ MCP RESULT RECEIVED:")
        print(data)
        
        # Verify if we got valid JSON
        if "{" in data or "[" in data:
            print("\n🎉 SUCCESS! The Dedalus MCP is talking to GitHub.")
        else:
            print("\n⚠️  Hmm, the AI might have just chatted instead of using the tool. Check the prompt.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())


async def fetch_commits_via_mcp():
    """
    High-level wrapper that returns a list of commits as dicts:
    [{"message": ..., "author_name": ..., "date": ...}, ...]
    """
    try:
        raw = await get_github_data_via_mcp()
        # If the MCP returned structured output (not a string), return it
        if isinstance(raw, list):
            return raw

        # Try to parse JSON string
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                # Fall through to a best-effort parse
                pass

        # If we get here, the MCP didn't return clean JSON
        print("⚠️  MCP response could not be parsed as JSON. Raw output below:")
        print(raw)
        return []

    except Exception as e:
        print(f"❌ MCP Error: {e}")
        return []