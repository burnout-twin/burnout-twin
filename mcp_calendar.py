import json
import minds_ai


async def get_calendar_data_via_mcp():
    """Ask the Calendar MCP for upcoming events.

    Expects an MCP like `issac/calendar-mcp` capable of reading the user's calendar.
    Returns raw result (string or structured) from the runner.
    """
    prompt = (
        "Use the Calendar tool to list upcoming calendar events for the next 3 days. "
        "Return a JSON list with fields: title, start, end, location, description."
    )
    result = await minds_ai.run_prompt(prompt, mcp_servers=["issac/calendar-mcp"])
    return result.output


async def fetch_calendar_via_mcp():
    try:
        raw = await get_calendar_data_via_mcp()
        if isinstance(raw, list):
            return raw
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        print("⚠️  Calendar MCP response couldn't be parsed as JSON. Raw output:")
        print(raw)
        return []
    except Exception as e:
        print(f"❌ Calendar MCP Error: {e}")
        return []
