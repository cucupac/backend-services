from app.dependencies import get_event_loop

# import task here


async def start_fee_update_task():
    loop = await get_event_loop()

    # stuff the task needs here

    # get_holdings_task = TaskNameHere()
    # loop.create_task(get_holdings_task.start_task())
