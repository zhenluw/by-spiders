import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from by.pipline import item


class Shop(item.Item):
    webid = item.Field()
    country = item.Field()
    shopid = item.Field()
    shopname = item.Field()
    icon = item.Field()
    url = item.Field()

    products = item.Field()
    followers = item.Field()
    following = item.Field()
    rating_num = item.Field()
    rating = item.Field()

    chatperformance = item.Field()
    joined_time = item.Field()
    abstract = item.Field()
    response_time = item.Field()
    create_time = item.Field()

    update_time = item.Field()
    create_by = item.Field()
    update_by = item.Field()
    login_user = item.Field()


def trans_shop(result):
    shop = Shop()
    for key in result.keys():
        try:
            shop[key] = result[key]
        except Exception:
            pass
    return shop


class Product(item.Item):
    webid = item.Field()
    country = item.Field()
    spu = item.Field()
    status = item.Field()
    product_title = item.Field()

    score = item.Field()
    ratings = item.Field()
    sold = item.Field()
    historical_sold = item.Field()
    price = item.Field()
    height_price = item.Field()
    min_price = item.Field()
    max_price = item.Field()

    quantity = item.Field()
    shopid = item.Field()
    category = item.Field()
    brand = item.Field()

    specifications = item.Field()
    description = item.Field()
    create_time = item.Field()
    update_time = item.Field()
    create_by = item.Field()

    update_by = item.Field()
    currency = item.Field()
    url = item.Field()
    shop_url  = item.Field()
    shipping_from = item.Field()
    shipping_cost = item.Field()

    cid1 = item.Field()
    cname1 = item.Field()
    cid2 = item.Field()
    cname2 = item.Field()
    cid3 = item.Field()
    cname3 = item.Field()


def trans_product(result):
    product = Product()
    for key in result.keys():
        try:
            product[key] = result[key]
        except Exception:
            pass
    return product


class SubProduct(item.Item):
    webid = item.Field()
    country = item.Field()
    spu = item.Field()
    sku = item.Field()
    status = item.Field()

    price = item.Field()
    quantity = item.Field()
    shopid = item.Field()
    sales_attributes = item.Field()
    create_time = item.Field()

    update_time = item.Field()
    create_by = item.Field()
    update_by = item.Field()
    url = item.Field()

    sold = item.Field()
    before_price = item.Field()


def trans_sub_product(result):
    subp = SubProduct()
    for key in result.keys():
        try:
            subp[key] = result[key]
        except Exception:
            pass
    return subp


class Task(item.Item):
    webid = item.Field()
    shopid = item.Field()
    shopname = item.Field()
    country = item.Field()
    spu = item.Field()
    sku = item.Field()
    parse_type = item.Field()
    level = item.Field()
    url = item.Field()
    sort = item.Field()
    page = item.Field()
    keyword = item.Field()


def trans_task(result):
    task = Task()
    for key in result.keys():
        try:
            task[key] = result[key]
        except Exception:
            pass
    return task


class Search(item.Item):
    webid = item.Field()
    country = item.Field()
    shopid = item.Field()
    keyword = item.Field()
    create_time = item.Field()
    update_time = item.Field()
    sort = item.Field()
    spu = item.Field()
    sold = item.Field()
    historical_sold = item.Field()
    position = item.Field()
    ad = item.Field()
    shipping_from = item.Field()


def trans_search(result):
    search = Search()
    for key in result.keys():
        try:
            search[key] = result[key]
        except Exception:
            pass
    return search


class ShopChange(item.Item):
    shopid = item.Field()
    shopname = item.Field()
    icon = item.Field()
    products = item.Field()
    followers = item.Field()

    following = item.Field()
    rating_num = item.Field()
    rating = item.Field()
    chatperformance = item.Field()
    abstract = item.Field()


def trans_shop_change(result):
    shop_change = ShopChange()
    for key in result.keys():
        try:
            shop_change[key] = result[key]
        except Exception:
            pass
    return shop_change


class ProductChange(item.Item):
    historical_sold = item.Field()
    price = item.Field()
    height_price = item.Field()
    product_title = item.Field()
    quantity = item.Field()


def trans_product_change(result):
    product_change = ProductChange()
    for key in result.keys():
        try:
            product_change[key] = result[key]
        except Exception:
            pass
    return product_change


class ProductSubChange(item.Item):
    sales_attributes = item.Field()
    price = item.Field()
    before_price = item.Field()
    sold = item.Field()
    quantity = item.Field()


def trans_product_sub_change(result):
    product_sub_change = ProductSubChange()
    for key in result.keys():
        try:
            product_sub_change[key] = result[key]
        except Exception:
            pass
    return product_sub_change

