import json
import asyncio
import os
from typing import Any, List, Dict, Optional

import minds_ai


async def _call_run_prompt(prompt: str, mcp_servers: List[str], timeout: int):
    coro = minds_ai.run_prompt(prompt, mcp_servers=mcp_servers)
    # support sync or async run_prompt implementations
    if asyncio.iscoroutine(coro):
        return await asyncio.wait_for(coro, timeout=timeout)
    return coro


def _normalize_track(item: Any) -> Dict:
    # Ensure a dict with expected fields
    if not isinstance(item, dict):
        return {"title": str(item), "artist": None, "album": None, "timestamp": None}
    return {
        "title": item.get("title") or item.get("name") or item.get("track") or item.get("song"),
        "artist": item.get("artist") or item.get("artists"),
        "album": item.get("album"),
        "timestamp": item.get("timestamp") or item.get("played_at") or item.get("time"),
        **{k: v for k, v in item.items() if k not in {"title", "artist", "album", "timestamp"}},
    }


async def get_spotify_data_via_mcp(
    mcp_servers: Optional[List[str]] = None, timeout: int = 15
) -> Any:
    """Ask the Spotify MCP for the user's current or recent tracks.

    Expects an MCP server like `issac/spotify-mcp` to be configured in Dedalus.
    Returns raw result (string or structured) from the runner.
    """
    prompt = (
        "Use the Spotify tool to return the user's currently playing track or "
        "most recent 5 played tracks. Return JSON list with fields: "
        "- title, -artist, -album, -timestamp"
    )
    if mcp_servers is None:
        env = os.environ.get("SPOTIFY_MCP", "issac/spotify-mcp")
        mcp_servers = [s.strip() for s in env.split(",") if s.strip()]
    try:
        result = await _call_run_prompt(prompt, mcp_servers=mcp_servers, timeout=timeout)
        return getattr(result, "output", result)
    except asyncio.TimeoutError:
        raise RuntimeError("Spotify MCP request timed out")
    except Exception as e:
        raise RuntimeError(f"Spotify MCP error: {e}")


async def fetch_spotify_via_mcp() -> List[Dict]:
    try:
        raw = await get_spotify_data_via_mcp()
        # If result already structured
        if isinstance(raw, list):
            return [_normalize_track(i) for i in raw]
        if isinstance(raw, dict):
            return [_normalize_track(raw)]
        if isinstance(raw, str):
            # try parse as JSON
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [_normalize_track(i) for i in parsed]
                if isinstance(parsed, dict):
                    return [_normalize_track(parsed)]
            except Exception:
                # attempt to extract JSON substring
                import re

                m = re.search(r"(\[.*\])", raw, re.DOTALL)
                if m:
                    try:
                        parsed = json.loads(m.group(1))
                        if isinstance(parsed, list):
                            return [_normalize_track(i) for i in parsed]
                    except Exception:
                        pass
        print("⚠️  Spotify MCP response couldn't be parsed as JSON. Raw output:")
        print(raw)
        return []
    except Exception as e:
        print(f"❌ Spotify MCP Error: {e}")
        return []


if __name__ == "__main__":
    # quick manual test runner
    async def _main():
        tracks = await fetch_spotify_via_mcp()
        print(json.dumps(tracks, indent=2, ensure_ascii=False))

    asyncio.run(_main())
