import json
import re

import scrapy

from PriceSpy.spiders.config import ShopConfig


class EnterSpider(scrapy.Spider):
    name = "enter"
    allowed_domains = ["enter.online"]

    shop = (ShopConfig()).findByName(name)
    start_urls = ["https://enter.online/telefoane/smartphone-uri"]

    def parse(self, response):
        print("URL: " + response.request.url)
        grid = response.xpath(
            "/html/body/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[1]/div[*]")
        # grid = response.xpath(
        #     "/html/body/div[4]/div[3]/div/div[2]/div[2]/div[3]/div[1]/div[*]")
        group = self.findGroupByLink(response.request.url)
        empty_page = True
        for el in grid:
            link = el.xpath("div/div[2]/a/@href").extract_first()
            if link is None:
                continue
            name = el.xpath(".//*[@class='product-title']/text()").extract_first()
            specs = el.xpath(".//*[@class='product-descr']/text()").extract_first()
            body = el.xpath("div/div[2]/a/@data-ga4").extract_first()
            data = json.loads(body)
            brand = data["ecommerce"]["items"][0]["item_brand"]
            price = int(data["ecommerce"]["items"][0]["price"])
            discount = int(data["ecommerce"]["items"][0]["discount"])
            current_price = price
            price = price + discount
            discount = current_price
            model = name
            category = group

            if category == 'PHONE':
                network_pattern = r'\b\d(G\+|G)\b'
                network = re.search(network_pattern, model)
                if network is not None:
                    index = model.find(network.group())
                    model = model[:index]
                    words = model.split()
                    model = (' '.join(words[1:])).strip()
                specsArray = specs.split('/')
                specs = specsArray[1].lower().strip().replace(" ", "")
            if category == "TV":
                model = model.split()[-1]
                specs = ''

            returnData = {
                "name": name,
                "model": model.strip(),
                "link": link,
                "price": price,
                "discount": discount,
                "brand": brand,
                "category": category,
                "specs": specs,
                "new": True,
                "shop": 'ENTER'
            }
            if current_price > 0:
                empty_page = False
                yield returnData

        next_page_xpath = "//*[@class='page-nav']/ul/li/*[@rel='next']/@href"
        next_page_el = response.xpath(next_page_xpath)
        # print("NextPage:",next_page)
        # next_page = response.css('a.next_page::attr(href)').get()
        if (next_page_el is not None):
            next_page = next_page_el.extract_first()
            if next_page is not None and empty_page is False:
                yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def findUrl(self, url):
        pattern = r'\?page=\d'
        match = re.search(pattern, url)
        if match is None:
            return url, True
        return url.replace(match.group(), ""), False

    def findGroupByLink(self, link):
        for item in self.shop["category"].items():
            if link.find(item[1]) != -1:
                return item[0]
        return None
