import redis
import json

import price_api

redis_c = redis.StrictRedis(host='localhost', port=5000, db=0)

def getCategories():
    categories_json = redis_c.get("categories")
    if categories_json is None:
        print("CATEGORIES FROM API")
        categories = price_api.getCategories()
        redis_c.set('categories',json.dumps(categories))
        return categories
    else:
        print("FROM REDIS")
        categories = json.loads(categories_json)
        return categories
    
def getBrandsByCategory(category):
    key = "CAT_"+category
    brands_json = redis_c.get(key)
    if brands_json is None:
        print("BRANDS FROM API")
        brands = price_api.getBrandsByCategory(category)
        redis_c.set(key,json.dumps(brands))
        return brands
    else:
        print("FROM REDIS")
        brands = json.loads(brands_json)
        return brands