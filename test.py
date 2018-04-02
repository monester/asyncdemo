import asyncio
from time import sleep
from datetime import datetime, timedelta


class Test:
    def __init__(self):
        self.stop = False

    async def poller(self):
        while True:
            print(f"polling in action: {self.stop}")
            await asyncio.sleep(5)
            print("polling done")


    async def main(self):
        polling = False
        coro = None
        while True:
            now = datetime.now()
            if not polling and now.second % 5 == 0:
                polling = True
                print("schedule poller in 5 seconds")
                coro = asyncio.ensure_future(self.poller())
                loop.call_later(5, lambda: coro)
            if now.second % 20 == 0:
                coro.cancel()
            #     print("SET STOP TO TRUE")
            #     self.stop = True
            # if coro:
            #     print(dir(coro))
            print(now, coro)
            await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(Test().main())
