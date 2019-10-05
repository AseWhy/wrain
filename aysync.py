import asyncio

def run_await(d):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(d)