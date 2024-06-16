import scrapy
from PriceSpy.spiders.config import ShopConfig
import json
import re


# pattern = r'^(?P<Brand>\w+)\s+(?P<Model>[\w\s\+]+)\s+(?P<Storage>\d+ (GB|TB))?(?P<Memory>\d+GB)?,?\s+(?P<Color>[\w\s]+)'
# pattern = r'^(?P<Brand>\w+)\s+(?P<Model>[\w\s\+]+)\s*((?P<Memory>\d+\s*(GB)*)\s*/\s*(?P<Storage>\d+\s*(GB|TB))|((?P<Mem>\d+\s*GB){0,1}\s+(?P<Sto>\d+\s*(GB|TB))))?,?\s+(?P<Color>[\w\s]+)'

class UltraSpider(scrapy.Spider):
    name = "ultra"
    allowed_domains = ["ultra.md"]
    shop = (ShopConfig()).findByName(name)

    # start_urls = ["https://ultra.md/category/" + item for item in list(shop["category"].values())]

    start_urls = [
        'https://ultra.md/category/smartphones'
    ]

    def parse(self, response):
        print("URL: " + response.request.url)
        card = response.xpath(
            "/html/body/div[1]/div[1]/main/div/section[1]/div/div/div[2]/div[2]/div[1]/div[*]/div/div")
        # print('Found: ', len(card))
        group = self.findGroupByLink(response.request.url)
        for el in card:
            path = el.xpath("div[1]/a/@href").extract_first()
            name = el.xpath("div[1]/a/text()").extract_first()
            discount = int(
                (el.xpath("div[2]/div[1]/div/div[last()]/div/span[1]/text()").extract_first()).strip().replace(" ", ""))
            priceArr = el.xpath("div[2]/div[1]/div/div[1]/span[1]/text()")
            if len(priceArr) == 0:
                price = discount
            else:
                price = int(priceArr.extract_first().strip().replace(" ", "").replace("\n", "").replace("lei", ""))

            product = self.extract_product_info(name, group)
            product["link"] = path
            product["price"] = price
            product["discount"] = discount
            product["category"] = group
            yield product

        getUrl, isFirst = self.findUrl(response.request.url)
        if isFirst:
            nrPageXpath = "/html/body/div[1]/div[1]/main/div/section[1]/div/div/div[2]/div[2]/div[3]/div/nav/div[2]/div[2]/span/span[last()-1]/button/text()"
            nrPagesX = response.xpath(nrPageXpath).extract_first()
            nrPages = int(nrPagesX.strip())
            for page in range(2, nrPages + 1):
                next_page = f'{getUrl}?page={page}'
                yield response.follow(next_page, callback=self.parse)

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

    def extract_product_info(self, name, category):
        brand = ''
        model = ''
        specs = ''
        color = ''
        if category == "PHONE":
            pattern = r"^(Telefon mobil|Smartphone) (.+?) ([^,]+), (.+)$"
            matches = re.findall(pattern, name)
            if matches:
                _, brand, model, specs = matches[0]
                storage = self.parseStorage(specs)
                if storage is not None:
                    specs = storage
            else:
                return
        if category == "TABLET":
            pattern = r"^(Tabletă) (.+?) ([^,]+), (.+)$"
            matches = re.findall(pattern, name)
            if matches:
                _, brand, model, specs = matches[0]
        if category == "SMARTWATCH":
            pattern = r"^(Ceas pentru copii|Ceas inteligent|Ceas Sport / Antrenament|Ceas Sport/Antrenament) (.+?) ([^,]+), (.+)$"
            matches = re.findall(pattern, name)
            if matches:
                _, brand, model, specs = matches[0]
        if category == "TV":
            process_name = name.replace("Televizor", "")
            pattern = r"^(.+?)\" (.+?) (SMART TV|SMART|TV) (.+?) (.+?), (.+)$"
            matches = re.findall(pattern, process_name)
            if matches:
                size, technology, tv_type, brand, model, specs = matches[0]
                technology.replace("Televizor", "")
                specs = ''
        if category == "LAPTOP":
            pattern = r"^(Laptop Gaming|Laptop Business|Laptop) (.+?)\" (.+?) (.+?), (.+)$"
            matches = re.findall(pattern, name)
            if matches:
                _, size, brand, model, specs = matches[0]
                specs += " " + size
        if category == "CONSOLE":
            pattern = r"^(Consolă de jocuri) (.+?) (.+?), (.+)$"
            matches = re.findall(pattern, name)
            if matches:
                _, brand, model, specs = matches[0]
        if category == "MONITOR":
            pattern = r"^(.+?)\" (Monitor|Monitor Gaming) (.+?) (.+?), (.+)$"
            matches = re.findall(pattern, name)
            if matches:
                size, _, brand, model, specs = matches[0]
                specs += " " + size
        if color != '':
            specs += " " + color
        return {
            "name": name,
            "model": model,
            "brand": brand,
            "category": category,
            "specs": specs,
            "new": True,
            "shop": 'ULTRA'
        }

    def parseStorage(self, name):
        name = name.lower()
        pattern = r'\d+gb/(\d+(gb|tb))'
        pattern2 = r'\b(32gb|64gb|128gb|256gb|512gb|1tb|2tb)'
        dictRss = re.search(pattern2, name)
        if dictRss is not None:
            storage = dictRss.group()
            # storage = dictRs
            # slash_index = storage.find("/")
            # if slash_index != -1:
            #     storage = dictRs[slash_index + 1:]
            # storage = storage.lower().strip()
            return storage
