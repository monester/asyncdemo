import os
import logging
import aiohttp
import asyncio
import async_timeout
import urllib

from avito_parser import AvitoHTMLParser, AvitoItemHTMLParser

avito_url = "https://www.avito.ru/rossiya?s=104&q="
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.text()


async def search(text):
    url = avito_url + urllib.parse.quote(text)
    log.debug(f"URL: {url}")

    html = await fetch(url)

    parser = AvitoHTMLParser()
    parser.feed(html)

    items = {i.id: i for i in parser.items}

    return items


import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open


class Chat:
    def __init__(self, chat_handler, chat_id):
        self.id = chat_id
        self.chat_handler = chat_handler
        self.search_filters = ['елочные игрушки']
        self.sent_items = set()
        self.coroutine = None
        self.initial_poll = True

    async def send_message(self, item):
        bot = self.chat_handler.sender
        await bot.sendMessage(text=f"{item.title} {item.address} {item.description} {item.price} {item.url}")
        if item.images:
            await bot.sendMediaGroup(media=[{
                'type': 'photo',
                'media': j,
            } for j in item.images])

    async def poller(self):
        while True:
            items = {}
            for text in self.search_filters:
                items.update(await search(text))

            if self.initial_poll:
                self.initial_poll = False
                self.sent_items = set(items.keys())

            new_items = items.keys() - self.sent_items
            log.debug(f'Sent items: {self.sent_items}')
            log.debug(f'New items: {new_items}')

            for item_id in new_items:
                item = items[item_id]

                AvitoItemHTMLParser(item).feed(await fetch(item.url))
                await asyncio.sleep(2)
                try:
                    await self.send_message(item)
                    self.sent_items.add(item_id)
                except:
                    pass

            await asyncio.sleep(10)

    def start(self):
        loop = asyncio.get_event_loop()
        self.coroutine = loop.create_task(self.poller())

    def stop(self):
        try:
            self.coroutine.cancel()
        except Exception as e:
            log.debug(e)


class MessageCounter(telepot.aio.helper.ChatHandler):
    _chats = {}

    async def on_chat_message(self, chat):
        cls = self.__class__
        text = chat['text']
        chat_id = chat['chat']['id']
        log.debug(f'CHAT ID: {chat_id}, message: {text}')

        if text.startswith('/start'):
            cls._chats[chat_id] = cls._chats.get(chat_id) or Chat(chat_handler=self, chat_id=chat_id)
            cls._chats[chat_id].start()
        elif text.startswith('/stop'):
            cls._chats[chat_id].stop()
        elif text.startswith('/reset'):
            cls._chats[chat_id].stop()
            del cls._chats[chat_id]
        elif text.startswith('/help'):
            await self.sender.sendMessage(text='+строка поиска')
        else:
            log.debug("Wrong message: ", text)


def main():
    bot = telepot.aio.DelegatorBot(TELEGRAM_TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, MessageCounter, timeout=10),
    ])

    loop = asyncio.get_event_loop()
    loop.create_task(MessageLoop(bot).run_forever())
    loop.run_forever()


if __name__ == '__main__':
    main()
