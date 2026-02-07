import os
from dedalus_labs import AsyncDedalus, DedalusRunner


def get_runner():
    """Return a DedalusRunner configured from env vars."""
    api_key = os.getenv("DEDALUS_API_KEY")
    client = AsyncDedalus(
        api_key=api_key,
        base_url=os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai"),
        as_base_url=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
    )
    return DedalusRunner(client)


async def run_prompt(prompt, model="openai/gpt-4o", mcp_servers=None):
    """Convenience wrapper to run a prompt via the Dedalus runner.

    Returns the Dedalus run result object (may have .output).
    """
    runner = get_runner()
    # Keep a sensible default timeout (seconds) for Dedalus calls
    timeout = 30

    async def _call():
        if mcp_servers is None:
            return await runner.run(input=prompt, model=model)
        return await runner.run(input=prompt, model=model, mcp_servers=mcp_servers)

    try:
        # Use asyncio.wait_for to enforce timeout
        import asyncio as _asyncio
        return await _asyncio.wait_for(_call(), timeout=timeout)
    except _asyncio.TimeoutError:
        raise RuntimeError(f"Dedalus call timed out after {timeout}s")
