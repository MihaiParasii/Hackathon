import scrapy
from PriceSpy.spiders.config import ShopConfig
from scrapy_requests import HtmlRequest
import re


class SmartSpider(scrapy.Spider):
    name = "smart"
    allowed_domains = ["www.smart.md"]
    default_url = "www.smart.md"
    shop = (ShopConfig()).findByName(name)

    # start_urls = ["https://www.smart.md/smartphone/" + item for item in list(shop["category"].values())]

    start_urls = [
        'https://www.smart.md/smartphone'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield HtmlRequest(url=url, callback=self.parse, render=True, options={'sleep': 2})

    async def parse(self, response):
        page = response.request.meta['page']
        #     # here I fetch data from it
        elements = response.xpath("//*[@id='pjaxy']/div/div[*]/div")
        group = self.findGroupByLink(response.request.url)
        for element in elements:
            name = element.xpath("a[2]/h4/text()").extract_first()
            product_url = element.xpath("a[2]/@href").extract_first()
            discount = element.xpath("div[2]/div[2]/h4/span/text()").extract_first()
            price = discount
            priceO = element.xpath("div[2]/div[2]/h4/del/text()")
            model = name
            storage = ""
            # print(name, price, discount)
            new = True

            if name.find("(Utilizat)") > -1:
                new = False
                name = name.replace("(Utilizat)", "").strip()
            if priceO is not None and len(priceO) != 0:
                price = priceO.extract_first()
            if group == 'PHONE':
                brand = name.split()[0]
                model, storage = self.parseNamePhone(name)
                battery_pattern = r'\b\d+(mAh)\b'
                model = re.sub(battery_pattern, '', model)
                network_pattern = r'\b\d(G\+|G)\b'
                model = re.sub(network_pattern, '', model)
                if brand == 'iPhone':
                    brand = "Apple"
                    model = "iPhone " + model
            if group == 'TV':
                brand, model = self.parseTVName(name)
            # if name == 'Xiaomi Poco F4 GT 5G Dual Sim 12/256GB, Black':
            #     print(name, price, discount)
            yield {
                "name": name,
                "model": model.strip(),
                "link": self.default_url + product_url,
                "price": int(price.replace("\xa0", "")),
                "discount": int(discount.replace("\xa0", "")),
                "brand": brand,
                "category": group,
                "specs": storage,
                "new": new,
                "shop": "SMART"

            }
        # allData = response.xpath("//*[@id='pjaxy']/div/div[*]/div/a[2]/h4/text()").extract()
        # for itemm in allData:
        #     yield {
        #         "name": itemm,
        #         "url": response.request.url
        #     }

        getUrl, pageNr = self.findUrl(response.request.url)
        offset = 32

        # PARALLEL-----PARALLEL-----PARALLEL-----PARALLEL-----PARALLEL-----PARALLEL-----PARALLEL-----PARALLEL-----PARALLEL-----
        # if pageNr == 0:
        #     number = self.getProductNumber(response)
        #     print("NR Total de elemente: " + str(number))
        #     pages = []
        #     if (number % offset == 0):
        #         pages = [getUrl + "?offset=" + str(i) for i in range(offset, number + 1, offset)]
        #     else:
        #         pages = [getUrl + "?offset=" + str(i) for i in range(offset, number + 1 + offset, offset)]
        #
        #     pages = pages[:-1]
        #
        #     for page in pages:
        #         yield HtmlRequest(url=page, callback=self.parse, render=True, options={'sleep': 20})

        # ITERATIVE-----ITERATIVE-----ITERATIVE-----ITERATIVE-----ITERATIVE-----ITERATIVE-----ITERATIVE-----
        nextPageNr = pageNr + offset
        number = self.getProductNumber(response)
        if nextPageNr < number:
            pageUrll = getUrl + "?offset=" + (str(nextPageNr))
            yield HtmlRequest(url=pageUrll, callback=self.parse, render=True, options={'sleep': 2})

        # print(response.body.decode('utf-8'))

    def getProductNumber(self, response):
        elements = self.getElements(response, "//*[@id='category_section']/div/div[1]/div/h1/text()")
        if len(elements) == 0:
            elements = self.getElements(response, "//*[@id='title_cat']/h1/text()")
        page_title = str(elements)
        number_str = re.search(r"\((\d+)\)", page_title).group(1)
        number = int(number_str)
        return number

    def getElements(self, tree, xpath):
        return tree.xpath(xpath).extract_first()

    def findUrl(self, url):
        pattern = r'\?offset=(\d+)'
        match = re.search(pattern, url)
        if match is None:
            return url, 0
        return url.replace(match.group(), ""), int(match.group(1))

    def findGroupByLink(self, link):
        for item in self.shop["category"].items():
            if link.find(item[1]) != -1:
                return item[0]
        return None

    def parseNamePhone(self, name):
        pattern = r'\b(\d+(?:/\d+)?(GB|gb|Gb|TB))\b'
        # pattern = r'^\d'
        dictRss = re.search(pattern, name)
        if dictRss is not None:
            dictRs = dictRss.group()
            storage = dictRs
            slash_index = storage.find("/")
            if slash_index != -1:
                storage = dictRs[slash_index + 1:]
            storage = storage.lower().strip().replace(" ", "")
            # storage = storage.replace("gb", "")
            # storage = storage.replace("Gb", "")
            index = name.find(dictRs)
            if index != -1:
                name = name[:index]
            words = name.split()
            model = (' '.join(words[1:])).strip()
            model = (model
                     .replace("Dual Sim", "")
                     .replace("DualSIM", "")
                     .replace("Dual SIM", "")
                     .replace(",", "")
                     .strip())
            return model, storage
        else:
            return None, None

    def parseTVName(self, name):
        if name == 'Televizor Philips OLED 55OLED907/12, 139 cm, Smart Android, 4K Ultra HD 100Hz, Clasa G':
            print("d")
        name = name.replace("Televizor / monitor", "").replace("Objet Collection Posé", "").replace("Televizon","")
        name = name.replace("BRAVIA", "").replace("Ambilight", "").replace("The One","").replace("AMBILIGHT","")
        name = name.replace("Display", "").replace("MultiSync", "").replace(".ADRB", "")
        name = name.replace("Televizor", "").replace("monitor",'').replace(",", "").replace('\\"', '').replace("Телевизор","")
        name = re.sub(r'\d+\s*cm', '', name)
        name = re.sub(r'/[A-Za-z]', '', name)
        name = re.sub(r'(/|\b)\d+"*(\s+|,)', ' ', name)
        name = re.sub(r'\b(LED|OLED|TV|SMART|Smart|NanoCell|QLED|FLEX|QNED|Neo|MiniLed|Mini|Led|LCD|4K|tv|Oled|MiniLED)\s', ' ', name)
        # name = re.sub(r'\s(LED|OLED|TV|SMART|Smart|NanoCell)\s', ' ', name)
        brand = name.split()[0].strip().capitalize()
        model = name.split()[1].strip()
        return brand, model
