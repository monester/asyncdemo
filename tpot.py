import os
import asyncio
import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open

class MessageCounter(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0

    async def on_chat_message(self, msg):
        self._count += 1
        await self.sender.sendMessage(self._count)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

bot = telepot.aio.DelegatorBot(TELEGRAM_TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=10),
])

# async def send():
#     await bot.sendMessage(chat_id=78219870, text="I'm a bot, please talk to me!")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(MessageLoop(bot).run_forever())
    # loop.create_task(send())
    print('Listening ...')
    loop.run_forever()
