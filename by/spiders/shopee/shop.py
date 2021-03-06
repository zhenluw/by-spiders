"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/27 16:43
"""

# 加入下面两行，requests请求不报错InsecureRequestWarning
import datetime
import traceback
import json
# 加入下面两行，requests请求不报错InsecureRequestWarning
import json_tools
import requests
import urllib3
urllib3.disable_warnings()
import sys
import os
import time
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.pipline.redisqueue import RedisQueue
from by.pipline.template import trans_shop, trans_task, trans_product, trans_sub_product, trans_shop_change, \
    trans_product_change, trans_product_sub_change
from by.utils.tools import DateEnconding, sleep_random_time1, sql_str_escape
from by.pipline.redisclient import RedisClient

cache_shop_insert = RedisQueue('cache_shop_insert', 'mz')
cache_shop_change_insert = RedisQueue('cache_shop_change_insert', 'mz')
cache_shop_update = RedisQueue('cache_shop_update', 'mz')
cache_shop_update_time = RedisQueue('cache_shop_update_time', 'mz')

cache_product_insert = RedisQueue('cache_product_insert', 'mz')
cache_product_change_insert = RedisQueue('cache_product_change_insert', 'mz')
cache_product_update = RedisQueue('cache_product_update', 'mz')
cache_product_update_time = RedisQueue('cache_product_update_time', 'mz')

cache_sub_product_insert = RedisQueue('cache_sub_product_insert', 'mz')
cache_sub_product_change_insert = RedisQueue('cache_sub_product_change_insert', 'mz')
cache_sub_product_update = RedisQueue('cache_sub_product_update', 'mz')

queue_shopee = RedisQueue('shopee', 'mz')
redis_db = RedisClient()


def get_html(url):
    sleep_random_time1()
    headers = {
        'referer': 'https://ph.xiapibuy.com/shop/283669838',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    }
    # return mayi.html_get(url, headers)
    return requests.get(url,headers=headers).text


# 商铺详情
def shop(task):
    shopid = task['shopid']
    try:
        url = "https://ph.xiapibuy.com/api/v4/shop/get_shop_detail?shopid={}&username=".format(shopid)
        # print(url)
        html = get_html(url)
        # print(html)
        json_str = json.loads(html)['data']

        shop = trans_shop(task)
        country = json_str['country']
        shop['country']= country
        shopid = json_str['shopid']
        shop['shopid']= shopid
        shop['shopname']= json_str['name']
        shop['icon']= 'https://cf.shopee.ph/file/{}_tn'.format(json_str['account']['portrait'])
        shop['products']= json_str['item_count']
        shop['followers']= json_str['follower_count']

        shop['following']= json_str['account']['following_count']
        rating_normal = json_str['rating_normal']
        rating_bad = json_str['rating_bad']
        rating_good = json_str['rating_good']
        shop['rating_num'] = int(rating_normal) + int(rating_bad) + int(rating_good)
        shop['rating']= json_str['rating_star']

        shop['chatperformance']= json_str['response_rate']
        joined_time = json_str['ctime']
        shop['joined_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(joined_time))

        # try:
        #     abstract = json_str['description']
        #     abstract = sql_str_escape(abstract)
        #     shop['abstract'] = abstract
        # except Exception:
        #     pass

        shop['abstract'] = ''

        shop['response_time']= json_str['preparation_time']
        shop['login_user'] = json_str['account']['username']

        try:
            flag = json_str['is_shopee_verified']
            if flag:
                shop['preferred'] = 1
            else:
                shop['preferred'] = 0
        except Exception:
            pass



        shop['url'] = 'https://ph.xiapibuy.com/shop/{}'.format(shopid)
        shop['create_time']= datetime.datetime.now()
        shop['create_by']= '007'

        shop_change(shop)
    except Exception as e:
        traceback.print_exc()
        print('shop异常--',e)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


# 店铺数据变更处理
def shop_change(shop):
    shop_change = trans_shop_change(shop)
    shop_id = shop['shopid']
    result = redis_db.hget("historical_shops",shop_id)
    if result is not None:
        # print('旧数据，比对')
        historical_shop = json.loads(result)
        change = json_tools.diff(dict(shop_change), historical_shop)
        if len(change) == 0:
            print('shopee_shope update time')
            cache_shop_update_time.put(shop_id)
        else:
            print('shopee_shope update，hopee_shope_change insert')
            cache_shop_update.put(json.dumps(dict(shop),cls = DateEnconding))
            cache_shop_change_insert.put(json.dumps(dict(shop),cls = DateEnconding))
    else:
        print('shopee_shope,shopee_shope_change insert')
        cache_shop_insert.put(json.dumps(dict(shop),cls = DateEnconding))

    # 无论是变更还是新增，都要同步到redis
    redis_db.hset('historical_shops',shop_id,json.dumps(dict(shop_change),cls = DateEnconding))

    # 传入队列内开始遍历商铺所有商品
    new_task = trans_task(shop)
    new_task['parse_type'] = 'goods_list'
    new_task['level'] = 1
    queue_shopee.put(json.dumps(dict(new_task),cls = DateEnconding))


# 商品列表
def product_list(task):
    shopid = task['shopid']
    try:
        level = task['level']
        if level ==1 :
            #  by= pop 流行  by= ctime 最新  by= sales 销量
            url = "https://ph.xiapibuy.com/api/v2/search_items/?by=sales&limit=30&match_id={}&newest=0&order=desc&page_type=shop&version=2".format(
                shopid)
            task['url'] = url
            total_count = product_list_parse(task)

            page_num = int(total_count/30)

            if page_num > 100:
                page_num = 100

            for i in range(1,page_num+1):
                url = "https://ph.xiapibuy.com/api/v2/search_items/?by=sales&limit=30&match_id={}&newest={}&order=desc&page_type=shop&version=2".format(
                    shopid,i*30)
                # print(url)
                new_task = trans_task(task)
                new_task['level'] = 2
                new_task['url'] = url
                queue_shopee.put(json.dumps(dict(new_task),cls = DateEnconding))
        else:
            product_list_parse(task)

    except Exception as e:
        traceback.print_exc()
        print('goods_list异常--',e)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


# 商品表解析
def product_list_parse(task):
    url = task['url']
    try:
        # print(url)
        html = get_html(url)
        # print(html)
        json_str = json.loads(html)
        total_count = json_str['total_count']
        for item in json_str['items']:
            new_task = trans_task(task)
            new_task['spu'] = item['itemid']
            new_task['parse_type'] = 'goods'
            historical_sold = item['historical_sold']

            # historical_sold 历史总销量为0，则抛弃
            if historical_sold == 0:
                continue
            queue_shopee.put(json.dumps(dict(new_task),cls = DateEnconding))

        return total_count
    except Exception as e:
        traceback.print_exc()
        print('goods_list异常--',e)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


# 商品详情
def product(task):
    itemid = task['spu']
    shopid = task['shopid']
    url=''
    try:
        url = "https://ph.xiapibuy.com/api/v2/item/get?itemid={}&shopid={}".format(itemid, shopid)
        html = get_html(url)
        # print(html)

        product = trans_product(task)

        item = json.loads(html)['item']

        product['sold'] = item['sold']
        product['historical_sold'] = item['historical_sold']

        product['url'] = 'https://ph.xiapibuy.com/product/{}/{}'.format(shopid,itemid)
        product['shop_url'] = 'https://ph.xiapibuy.com/shop/{}'.format(shopid)
        product['spu'] = item['itemid']
        product_title = item['name']
        product_title = sql_str_escape(product_title)

        product['product_title'] = product_title
        product['score'] = item['item_rating']['rating_star']

        product['ratings'] = item['cmt_count']

        try:
            price_min = item['price_min']
            product['price'] = int(price_min)/100000
        except Exception:
            pass

        try:
            price_max = item['price_max']
            product['height_price'] = int(price_max)/100000
        except Exception:
            pass

        try:
            price_min_before_discount = item['price_min_before_discount']
            if price_min_before_discount <= 0:
                price_min_before_discount = 0

            product['min_price'] = int(price_min_before_discount)/100000
        except Exception:
            pass

        try:
            price_max_before_discount = item['price_max_before_discount']
            if price_max_before_discount <= 0:
                price_max_before_discount = 0
            product['max_price'] = int(price_max_before_discount)/100000
        except Exception:
            pass

        product['quantity'] = item['stock']

        product['shopid'] = item['shopid']

        try:
            for brands in item['attributes']:
                brand_name = brands['name']
                brand_value = brands['value']
                if 'Brand' in brand_name:
                    brand = brand_value
            brand = sql_str_escape(brand)
            product['brand'] = brand
        except Exception:
            pass

        cats = []
        for categorie in item['categories']:
            catid = categorie['catid']
            display_name = categorie['display_name']
            cats.append({
                "catid":catid,
                "display_name":display_name
            })

        try:
            product['cid1'] = item['categories'][0]['catid']
            display_name = item['categories'][0]['display_name']
            display_name = sql_str_escape(display_name)
            product['cname1'] = display_name
        except Exception:
            pass

        try:
            product['cid2'] = item['categories'][1]['catid']
            display_name = item['categories'][1]['display_name']
            display_name = sql_str_escape(display_name)
            product['cname2'] = display_name
        except Exception:
            pass

        try:
            product['cid3'] = item['categories'][2]['catid']
            display_name = item['categories'][2]['display_name']
            display_name = sql_str_escape(display_name)
            product['cname3'] = display_name
        except Exception:
            pass

        try:
            ctime = item['ctime']
            product['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ctime))
        except Exception:
            pass

        product['flash_deals'] = 0
        try:
            upcoming_flash_sale = item['upcoming_flash_sale']
            if upcoming_flash_sale:
                product['flash_deals'] = 1
        except Exception:
            pass

        product['view_count'] = 0
        try:
            view_count = item['view_count']
            if view_count:
                product['view_count'] = view_count
        except Exception:
            pass


        # description = item['description']
        # description = sql_str_escape(description)
        # product['description'] = ''

        product['status'] = 1

        attributes = json.dumps(item['attributes'])
        attributes = sql_str_escape(attributes)
        product['specifications'] = attributes
        product['currency'] = item['currency']

        product['shipping_from'] = item['shop_location']
        # product['shipping_cost'] = ''

        product['create_time']= datetime.datetime.now()
        product['create_by']= '007'

        # 商品数据变更处理
        product_change(product,item)
    except Exception as e:
        traceback.print_exc()
        print('goods异常--',e,url)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


# 商品数据变更处理
def product_change(product,item):
    product_change = trans_product_change(product)
    spu = product['spu']
    result = redis_db.hget("historical_product",spu)
    if result is not None:
        # print('旧数据，比对')
        historical_product = json.loads(result)
        change = json_tools.diff(dict(product_change), historical_product)
        if len(change) == 0:
            print('shopee_product update_time')
            cache_product_update_time.put(spu)
        else:
            print('shopee_product update，shopee_product_change insert')
            cache_product_update.put(json.dumps(dict(product),cls = DateEnconding))
            cache_product_change_insert.put(json.dumps(dict(product),cls = DateEnconding))

        # 子产品处理
        good_sub_old(item,product)
    else:
        print('shopee_product insert')
        cache_product_insert.put(json.dumps(dict(product),cls = DateEnconding))

        # 子产品处理
        good_sub_new(item,product)

    redis_db.hset('historical_product',spu,json.dumps(dict(product_change),cls = DateEnconding))


# 子商品new
def good_sub_new(json_str,product):
    for model in json_str['models']:
        sub_product = sub_entity(model,product)
        product_sub_change = trans_product_sub_change(sub_product)
        spu = sub_product['spu']
        sku = sub_product['sku']
        key = '{}{}'.format(spu,sku)
        cache_sub_product_insert.put(json.dumps(dict(sub_product),cls = DateEnconding))
        redis_db.hset('historical_product_sub',key,json.dumps(dict(product_sub_change),cls = DateEnconding))


# 子商品old
def good_sub_old(json_str,product):
    for model in json_str['models']:
        sub_product = sub_entity(model,product)

        product_sub_change = trans_product_sub_change(sub_product)
        spu = sub_product['spu']
        sku = sub_product['sku']
        key = '{}{}'.format(spu,sku)
        result = redis_db.hget("historical_product_sub",key)
        if result is not None:
            # print('旧数据，比对')
            historical_product_sub = json.loads(result)
            change = json_tools.diff(dict(product_sub_change), historical_product_sub)
            if len(change) == 0:
                # print('数据未变动,不做任何操作')
                print()
            else:
                # print('数据变动,更新 shopee_sub_product，并插入 shopee_sub_product_change 一条变更后新数据')
                # status = 1 为了遇到曾经下架再次上架的商品，进行状态的改变
                status = 1
                quantity = product['quantity']
                if quantity == 0:
                    status = 0
                sub_product['status'] = status

                cache_sub_product_update.put(json.dumps(dict(sub_product),cls = DateEnconding))
                cache_sub_product_change_insert.put(json.dumps(dict(sub_product),cls = DateEnconding))

        else:
            cache_sub_product_insert.put(json.dumps(dict(sub_product),cls = DateEnconding))

        redis_db.hset('historical_product_sub',key,json.dumps(dict(product_sub_change),cls = DateEnconding))


# 组装sub实体
def sub_entity(model,product):
    sub_product = trans_sub_product(product)
    spu = model['itemid']
    sub_product['spu'] = spu
    sku = model['modelid']
    sub_product['sku'] = sku
    sub_product['url'] = 'https://ph.xiapibuy.com/product/{}/{}?sku={}'.format(product['shopid'],spu,sku)
    try:
        price = model['price']
        if price <= 0:
            price = 0
        sub_product['price'] = int(price)/100000
    except Exception:
        pass

    sub_product['before_price'] = 0
    try:
        price_before_discount = model['price_before_discount']
        if price_before_discount <= 0:
            price_before_discount = 0
        sub_product['before_price'] = int(price_before_discount)/100000
    except Exception:
        pass
    sub_product['sold'] = model['sold']
    status = 1
    try:
        quantity = model['stock']
        sub_product['quantity'] = quantity
        if quantity == 0:
            status = 0
    except Exception:
        pass
    sub_product['status'] = status
    sub_product['sales_attributes'] = model['name']
    sub_product['create_time']= datetime.datetime.now()
    sub_product['create_by']= '007'

    return sub_product


if __name__ == '__main__':
    task={
        "shopid":'283669838',
        "parse_type":"shop",
        "webid":1,
        "level": 1,
        "country": "PH",
    }
    # queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))
    # shop(task)

    task={"shopid": 283669838, "webid": 1, "country": "PH", "shopname": "T1 Summer", "url": "https://ph.xiapibuy.com/shop/283669838", "parse_type": "goods_list", "level": 1}
    # product_list(task)

    task= {"shopid": 283669838, "webid": 1, "country": "PH", "shopname": "T1 Summer", "url": "https://ph.xiapibuy.com/api/v2/search_items/?by=pop&limit=30&match_id=283669838&newest=0&order=desc&page_type=shop&version=2", "parse_type": "goods", "level": 1, "spu": 7543532138}
    # product(task)
