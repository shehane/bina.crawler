import json
import re
from urllib.request import Request, urlopen

import scrapy
from scrapy.http import Response
from scrapy.spiders import Spider

from bina.items import ListingItem, BinaItem


class BinaListingSpider(Spider):
    name = 'bina.az'
    start_urls = ['https://bina.az/alqi-satqi/menziller/yeni-tikili',
                  'https://bina.az/baki/alqi-satqi/menziller/kohne-tikili']
    MAX_PAGES_TO_CRAWL = 50
    custom_settings = {
        'FEED_URI': './listings.json',
        'FEED_FORMAT': 'json',
        'FEED_EXPORTERS': {
            'json': 'scrapy.exporters.JsonItemExporter',
        },
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def parse(self, response: Response, **cb_kwargs):
        selection = response.css('.vipped-apartments~ .items_list > .items-i')
        # selection = response.css('.items-i >.item_link')
        for bina_listing in selection:
            yield ListingItem({
                'name': bina_listing.css('.items-i .card_params .location::text').get(),
                'url': bina_listing.css('.item_link').attrib['href'],
            })

        next_url_selector = response.css(".next a")

        if len(next_url_selector) <= 0:
            return

        next_url_href = next_url_selector.attrib["href"]
        next_page = int(next_url_href.split('=')[1])

        if not self.crawling_limit_reached(next_page):
            self.logger.info("Next URL: %s", next_url_href)
            yield response.follow(next_url_href, callback=self.parse)

    def crawling_limit_reached(self, page):
        return page >= self.MAX_PAGES_TO_CRAWL





class BinaSpider(Spider):
    name = 'flats'
    custom_settings = {
        'FEED_URI': './flats.json',
        'FEED_FORMAT': 'json',
        'FEED_EXPORTERS': {
            'json': 'scrapy.exporters.JsonItemExporter',
        },
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open('./listings.json', encoding='utf-8') as data_file:
            self.data = json.load(data_file)

    def start_requests(self):
        for item in self.data:
            flat_url = 'https://bina.az' + item['url']
            request = scrapy.Request(flat_url, callback=self.parse)
            request.meta['item'] = item
            yield request

    def parse(self, response: Response, **kwargs):
        item = {}
        title = response.css('h1::text').get()
        price = response.css('.price-val::text').get()
        currency = response.css('.price-cur::text').get()
        price_per_sm = response.css('.unit-price::text').get()
        description = response.css('.side p ::text').get()
        address = response.css('.map_address::text').get()
        date_added = response.css('p~ p+ p ::text').get()
        room_number = response.css('tr:nth-child(4) td:nth-child(2)::text').get()
        area = response.css('tr:nth-child(3) td:nth-child(2)::text').get()
        stage = response.css('tr:nth-child(2) td:nth-child(2)::text').get()
        images = response.css('.large-photo img').attrib['src']
        url = response.url
        kupcha = response.css('tr:nth-child(5) td:nth-child(2)::text').get()
        ipoteka = response.css('tr:nth-child(6) td:nth-child(2)::text').get()
        name = response.css('.contacts>.name::text').get()
        number = response.css('#show-phones span+ span::text').get()
        occupation = response.css('.ownership::text').get()
        category = response.css('tr:nth-child(1) td:nth-child(2)').get()
        coordinates = response.css('.open_map img').attrib['data-src']

        yield BinaItem({
            'title': title,
            'price': price,
            'currency': currency,
            'price_per_sm': price_per_sm,
            'description': description,
            'address': address,
            'date_added': date_added,
            'room_number': room_number,
            'area': area,
            'stage': stage,
            'images': images,
            'url': url,
            'kupcha': kupcha,
            'ipoteka': ipoteka,
            'name': name,
            'number': number,
            'occupation': occupation,
            'category': category,
            'latitude': re.findall('%2C(.+?)&', coordinates),
            'longtitude': re.findall('markers=(.+?)%', coordinates)

            })
