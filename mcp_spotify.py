import json
import asyncio
import minds_ai


async def get_spotify_data_via_mcp():
    """Ask the Spotify MCP for the user's current or recent tracks.

    Expects an MCP server like `issac/spotify-mcp` to be configured in Dedalus.
    Returns raw result (string or structured) from the runner.
    """
    prompt = (
        "Use the Spotify tool to return the user's currently playing track or "
        "most recent 5 played tracks. Return JSON list with fields: "
        "- title, -artist, -album, -timestamp"
    )
    # Replace the mcp server name below if your MCP is different
    result = await minds_ai.run_prompt(prompt, mcp_servers=["issac/spotify-mcp"])
    return result.output


async def fetch_spotify_via_mcp():
    try:
        raw = await get_spotify_data_via_mcp()
        if isinstance(raw, list):
            return raw
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        print("⚠️  Spotify MCP response couldn't be parsed as JSON. Raw output:")
        print(raw)
        return []
    except Exception as e:
        print(f"❌ Spotify MCP Error: {e}")
        return []
