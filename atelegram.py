import os
import asyncio
import aiohttp
import logging

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Telegram:
    def __init__(self, token, loop=None):
        self.token = token
        self.loop = loop or asyncio.get_event_loop()
        self.coro = asyncio.ensure_future(self.get_updates())

    async def get(self, call):
        url = f'https://api.telegram.org/bot{self.token}/{call}'
        log.debug('get: %s', url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def get_updates(self):
        messages = []
        while True:
            call = 'getUpdates?timeout=5'
            try:
                if messages:
                    call = f'{call}&offset={messages[-1]['update_id']+1}'
                result = await self.get(call)
                messages.extend(result['result'])

                log.debug('Got messages: %s (total: %s)', len(result['result']), len(messages))
                for i in result['result']:
                    log.debug('Text: %s', i['message']['text'])
            except Exception as e:
                print(messages[-1])
                log.exception(e)
                await asyncio.sleep(3)
                raise
            log.debug("GET UPDATES")


async def get_me():
    t = Telegram(TELEGRAM_TOKEN)

    while True:
        await asyncio.sleep(1)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_me())


if __name__ == '__main__':
    main()
