import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner

async def main():
    client = AsyncDedalus(api_key="dsk-test-23ff970dac62-9b28b63193a4223dfb297963c91dbae9")
    runner = DedalusRunner(client)

    response = await runner.run(
        input="Hello, what can you do?",
        model="anthropic/claude-opus-4-5",
    )
    print(response.final_output)

asyncio.run(main())