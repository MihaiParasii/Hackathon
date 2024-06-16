import scrapy
from PriceSpy.spiders.config import ShopConfig
import json
import re
from scrapy_requests import HtmlRequest


# pattern = r'^(?P<Brand>\w+)\s+(?P<Model>[\w\s\+]+)\s+(?P<Storage>\d+ (GB|TB))?(?P<Memory>\d+GB)?,?\s+(?P<Color>[\w\s]+)'
# pattern = r'^(?P<Brand>\w+)\s+(?P<Model>[\w\s\+]+)\s*((?P<Memory>\d+\s*(GB)*)\s*/\s*(?P<Storage>\d+\s*(GB|TB))|((?P<Mem>\d+\s*GB){0,1}\s+(?P<Sto>\d+\s*(GB|TB))))?,?\s+(?P<Color>[\w\s]+)'

class DarwinSpider(scrapy.Spider):
    name = "darwin"
    allowed_domains = ["darwin.md"]
    baseUrl = "https://darwin.md/"
    shop = (ShopConfig()).findByName(name)

    # start_urls = ["https://darwin.md/" + item for item in list(shop["category"].values())]

    start_urls = [
        'https://darwin.md/telefoane'
    ]

    def start_requests(self):
        for url in self.start_urls:
            # yield scrapy.Request(url=url, headers={'Cache-Control': 'no-cache'})
            yield HtmlRequest(url=url, callback=self.parse, render=True, options={'sleep': 2})

    def parse(self, response):
        print("URL: " + response.request.url)
        grid = response.xpath(
            "//*[@id='main']/section[@class='products']/div/div/div/div[*]/figure")
        # allData2 = grid.xpath("div[@class='grid-item']/div/a/@data-ga4").getall()
        # allData = response.xpath(
        #     "/html/body/main/section[@class='products']/div/div/div/div/figure/div[@class='grid-item']/div/a/@data-ga4").getall()

        group = self.findGroupByLink(response.request.url)
        empty_page = True
        for el in grid:
            exists_xpath = el.xpath("div[1]/text()")
            if exists_xpath is not None:
                if exists_xpath.extract_first().find("epuizat") > -1:
                    continue
            data_grid = el.xpath("div[@class='grid-item']/div/a")
            rsss = self.parseData(data_grid, group)
            if rsss is not None:
                empty_page = False
                print(response.request.url, rsss)
                yield rsss

        next_page_xpath = '//*[@id="main"]/section[3]/div/div/div/div[21]/section/div/div/div/nav/ul/li[last()]/a'
        next_page_el = response.xpath(next_page_xpath)
        # print("NextPage:",next_page)
        # next_page = response.css('a.next_page::attr(href)').get()
        if (next_page_el is not None) and ('href' in next_page_el.attrib):
            next_page = next_page_el.attrib['href']
            if next_page:
                if not empty_page:
                    yield HtmlRequest(url=response.urljoin(next_page), callback=self.parse, render=True,
                                      options={'sleep': 2})
                # yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def parseData(self, el, group):
        allData2 = el.xpath("@data-ga4").extract_first()
        href = el.xpath("@href").extract_first()
        data = json.loads(allData2)
        name = data["ecommerce"]["items"][0]["item_name"]
        modeld = None
        storage = None
        if group == 'PHONE':
            modeld, storage = self.parseNamePhone(name)
        if group == 'TV':
            modeld = self.parseTVName(name)

        model = modeld if modeld is not None else name
        link = href
        price = int(data["ecommerce"]["items"][0]["price"])
        discount = int(data["ecommerce"]["items"][0]["discount"])
        brand = data["ecommerce"]["items"][0]["item_brand"]
        category = group
        specs = data["ecommerce"]["items"][0]["item_variant"]
        if group == 'PHONE':
            if storage is not None:
                specs = storage.replace(" ", "")
        if group == 'TV':
            specs = ''
        # if group == 'PHONE' and name.find('iPad') > -1:
        #     print("ERROR")
        current_price = price
        price = price + discount
        discount = current_price
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
            "shop": 'DARWIN'
        }
        # print(returnData)
        if current_price > 0:
            return returnData
        return None

    def findGroupByLink(self, link):
        for item in self.shop["category"].items():
            if link.find(item[1]) != -1:
                return item[0]
        return None

    def parseNamePhone(self, name):
        pattern = r'((?P<Memory>\d+\s*(GB)*)\s*/\s*(?P<Storage>\d+\s*(GB|TB))|((?P<Mem>\d+\s*GB){0,1}\s+(?P<Sto>\d+\s*(GB|TB))))'
        # pattern = r'^\d'
        dictRss = re.search(pattern, name)
        if dictRss is not None:
            dictRs = dictRss.groupdict()
            storage = dictRs["Storage"] if dictRs["Storage"] is not None else dictRs["Sto"]
            index = name.find(storage)
            if index != -1:
                name = name[:index]
            words = name.split()
            model = (' '.join(words[1:])).strip()
            network_pattern = r'\b\d(G\+|G)\b'
            model = re.sub(network_pattern, '', model)
            model.strip()
            storage = storage.lower().strip()
            return model, storage
        else:
            return None, None

    def parseTVName(self, name):
        model = name.split()[3]
        return model
