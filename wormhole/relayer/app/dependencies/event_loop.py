import asyncio
from asyncio import AbstractEventLoop

import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


loop = None


async def get_event_loop() -> AbstractEventLoop:
    global loop  # pylint: disable = global-statement
    if loop is None:
        loop = asyncio.get_event_loop()
    return loop
