# config.py
import os
import json

def read_json_file(file_path):
    try:
        # print("Path:", os.getcwd())
        # file_path = os.path.join(os.path.dirname(__file__), '../../data/shop_config.json')
        # Open the JSON file and load its content into a Python dictionary
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error occurred while reading the JSON file: {e}")
        return None


# class Shop:
#     def __init__(self, name, url, javascript, category):
#         self.name = name
#         self.url = url
#         self.javascript = javascript
#         self.category = category

# def getShops(data):
#     shops_data = data['shop']
#     shops = []
#     for shop_data in shops_data:
#         shop = Shop(
#             name=shop_data['name'],
#             url=shop_data['url'],
#             javascript=shop_data['javascript'],
#             category=shop_data['category']
#         )
#         shops.append(shop)
#     return shops


class ShopConfig:
    SHOPS_CONFIG_FILE = "PriceSpy/spiders/config/shop_config.json"
    def __init__(self):
        self.SHOPS_DATA_MAP = read_json_file(ShopConfig.SHOPS_CONFIG_FILE)
        if self.SHOPS_DATA_MAP == None:
            print("can't read")
  
    def findByName(self, name):
        for item in self.SHOPS_DATA_MAP['shop']:
            if item['name'] == name:
                return item




