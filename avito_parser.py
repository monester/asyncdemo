import logging

from html.parser import HTMLParser
from models import Item

AVITO_URL = 'https://www.avito.ru'
log = logging.getLogger(__name__)


class BaseAvitoHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
        self.item = None
        self._section = []
        self._depth = []
        self.ignore_tags = ['img', 'br']

    @property
    def section(self):
        return self._section and self._section[-1] or None

    @section.setter
    def section(self, section):
        self._section.append(section)
        self._depth.append(0)
        # print(f">> Add {section} on depth 0")

    @section.deleter
    def section(self):
        section = self._section.pop()
        depth = self._depth.pop()
        # print(f"<< Removed {section} on depth {depth}")

    @property
    def depth(self):
        return self._depth and self._depth[-1] or 0

    @depth.setter
    def depth(self, value: int):
        if self._depth:
            if value == 0:
                del self.section
            else:
                self._depth[-1] = value

    # def reset(self):
    #     self._section = []
    #     self._depth = []


class AvitoHTMLParser(BaseAvitoHTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag_class = attrs.get('class', '')
        if tag_class.startswith('item item_table'):
            self._section = []
            self._depth = []
            # print("----- START OF ITEM:", tag)
            self.section = 'root'
            self.item = Item(attrs['id'])

        if self.item:
            # different images
            if tag_class == "item-slider-image large-picture":
                self.item.images.append("https:" + attrs['style'][22:-1])
            if tag_class == "item-slider-image js-lazy large-picture":
                self.item.images.append("https:" + attrs['data-srcpath'])
            if tag_class == 'photo-count-show large-picture':
                self.item.images.append("https:" + attrs['src'])

            # title of item
            if tag_class == "item-description-title-link":
                self.section = 'title'
                self.item.url = AVITO_URL + attrs['href']

            if tag_class == "data":
                self.section = 'data'

            if self.section == 'data' and tag == 'p':
                self.section = tag

            if tag not in self.ignore_tags:
                self.depth += 1

    def handle_data(self, data):
        data = data.strip()

        if self.section == 'title':
            self.item.title = data

        if self._section[-2:] == ['data', 'p']:
            self.item.data.append(data)

    def handle_endtag(self, tag):
        if tag not in self.ignore_tags:
            self.depth = self.depth - 1

        if self.section is None and self.item:
            # print("----- END OF ITEM:", tag)
            self.items.append(self.item)
            self.item = None


class AvitoItemHTMLParser(BaseAvitoHTMLParser):
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.prop = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag_class = attrs.get('class', '')
        if tag_class == 'price-value-string js-price-value-string':
            self.section = 'price'

        if tag_class == 'seller-info-name':
            self.section = 'seller-info-name'

        if attrs.get('itemprop') == "description":
            self.section = 'description'
            self.item.description = ''

        # if attrs.get('itemprop') == 'address':
        if tag_class == 'item-map-location':
            self.section = 'address'

        if self.section and tag not in self.ignore_tags:
            self.depth += 1

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        if self.section == 'price':
            if self.depth == 1:
                self.item.price = data
            elif self.depth == 3:
                self.item.price += data

        if self.section == 'seller-info-name' and self.depth == 2:
            self.item.contact = data

        if self.section == 'description':
            self.item.description += data

        if self.section == 'address':
            self.item.address += data

    def handle_endtag(self, tag):
        if tag not in self.ignore_tags:
            self.depth = self.depth - 1


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
    log.setLevel(logging.DEBUG)
    # with open('avito_item.html', encoding='utf-8') as f:
    #     html = f.read()
    #
    # item = Item(id=1)
    # AvitoItemHTMLParser(item).feed(html)
    #
    # print(repr(item))
    import urllib
    import urllib.request
    import time

    with urllib.request.urlopen('https://www.avito.ru/rossiya?q=%D0%B8%D0%B3%D1%80%D1%83%D1%88%D0%BA%D0%B8') as response:
        print(response.code)
        html = response.read().decode('utf-8')

    print(html)
    parser = AvitoHTMLParser()
    parser.feed(html)

    for i in parser.items:
        time.sleep(2)
        with urllib.request.urlopen(i.url) as response:
            html = response.read().decode('utf-8')
        AvitoItemHTMLParser(i).feed(html)
        print(repr(i))
