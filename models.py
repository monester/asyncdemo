import textwrap
import asyncio
import aioodbc


class Item:
    items = {}

    def __init__(self, id):
        self.id = id
        self.title = ''
        self.section = ''
        self._address = ''
        self.description = ''
        self.price = None
        self.contact = ''
        self.images = []
        self.data = []
        self._url = ''

    def __repr__(self):
        return textwrap.dedent(f"""\
        <Item id={self.id}
            contact={self.contact}
            address={self.address}
            description={self.description}
            price={self.price}
            url={self.url}
            title={self.title}
            images={self.images}
            data={self.data}
        />""")

    @classmethod
    async def get(cls, id):
        # dsn = 'Driver=SQLite;Database=sqlite.db'
        # loop = asyncio.get_event_loop()
        #
        # async with aioodbc.create_pool(dsn=dsn, loop=loop) as pool:
        #     async with pool.acquire() as conn:
        #         async with conn.cursor() as cur:
        #             await cur.execute('SELECT 42 AS age;')
        #             val = await cur.fetchone()
        #             print(val)
        #             print(val.age)
        # return cls(
        #     id
        # )
        return cls.items.get(id)

    async def save(self, id):
        self.__class__.items[id] = self

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url if url.startswith('http') else f'https://www.avito.ru{url}'

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        address = address.replace('Адрес:', '').replace('Посмотреть карту', '')
        self._address = address
