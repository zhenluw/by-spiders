import traceback

from by.pipline import item


class Shop(item.Item):
    webid = item.Field()
    country = item.Field()
    shopid = item.Field()
    shopname = item.Field()
    icon = item.Field()

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
    price = item.Field()
    height_price = item.Field()

    quantity = item.Field()
    login_user = item.Field()
    shopid = item.Field()
    category = item.Field()
    brand = item.Field()

    specifications = item.Field()
    description = item.Field()
    create_time = item.Field()
    update_time = item.Field()
    create_by = item.Field()

    update_by = item.Field()


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


def trans_sub_product(result):
    subp = SubProduct()
    for key in result.keys():
        try:
            subp[key] = result[key]
        except Exception:
            pass
    return subp


class Task(item.Item):
    shopid = item.Field()
    shopname = item.Field()
    country = item.Field()
    spu = item.Field()
    sku = item.Field()
    parse_type = item.Field()
    level = item.Field()
    url = item.Field()


def trans_task(result):
    task = Task()
    for key in result.keys():
        try:
            task[key] = result[key]
        except Exception:
            pass
    return task



