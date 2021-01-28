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
from by.utils.tools import DateEnconding, sleep_random_time1
from by.pipline import dbpool
from by.pipline.redisclient import RedisClient

queue_shopee = RedisQueue('shopee', 'mz')
redis_db = RedisClient(11)


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
        print(url)
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

        try:
            abstract = json_str['description']
            abstract = abstract.replace("'", "''")
            abstract = abstract.replace('"', '""')
            shop['abstract'] = abstract
        except Exception:
            pass

        shop['response_time']= json_str['preparation_time']
        shop['login_user'] = json_str['account']['username']

        shop['url'] = 'https://ph.xiapibuy.com/shop/{}'.format(shopid)
        shop['create_time']= datetime.datetime.now()
        shop['create_by']= '007'

        shop_change(shop)
    except Exception as e:
        traceback.print_exc()
        print('shop异常--',e)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))
    print('存入redis队列')


# 店铺数据变更处理
def shop_change(shop):
    shop_change = trans_shop_change(shop)
    shop_id = shop['shopid']
    result = redis_db.hget("historical_shops",shop_id)
    if result is not None:
        print('旧数据，比对')
        historical_shop = json.loads(result)
        change = json_tools.diff(dict(shop_change), historical_shop)
        if len(change) == 0:
            print('数据未变动,只需要改动shopee_shope update_time')
            sql = "update shopee_shope set update_time=%s , update_by= %s where shopid= %s"
            now_time = datetime.datetime.now()
            dbpool.Pool().update(sql,(now_time,'007',shop_id))
        else:
            print('数据变动,更新shopee_shope，并插入shopee_shope_change一条变更后新数据')
            sql = "update shopee_shope set " \
                  "shopname=%s ," \
                  "icon=%s ," \
                  "products=%s ," \
                  "followers=%s ," \
                  "following=%s ," \
                  "rating_num=%s ," \
                  "rating=%s ," \
                  "chatperformance=%s ," \
                  " abstract=%s ," \
                  " update_time=%s ," \
                  " update_by= %s" \
                  " where shopid= %s"

            params = (shop['shopname'],
                      shop['icon'],
                      shop['products'],
                      shop['followers'],
                      shop['following'],
                      shop['rating_num'],
                      shop['rating'],
                      shop['chatperformance'],
                      shop['abstract'],
                      datetime.datetime.now(),
                      '007',
                      shop_id)
            dbpool.Pool().update(sql,params)
            dbpool.Pool().insert_temp('shopee_shope_change', shop,'shopee_shope_change')
    else:
        print('新数据，入库shopee_shope,shopee_shope_change,并同步到historical_shops')
        dbpool.Pool().insert_temp('shopee_shope', shop,'shopee_shope')
        dbpool.Pool().insert_temp('shopee_shope_change', shop,'shopee_shope_change')

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
            url = "https://ph.xiapibuy.com/api/v2/search_items/?by=pop&limit=30&match_id={}&newest=0&order=desc&page_type=shop&version=2".format(
                shopid)
            task['url'] = url
            total_count = product_list_parse(task)

            page_num = int(total_count/30)
            for i in range(1,page_num+1):
                url = "https://ph.xiapibuy.com/api/v2/search_items/?by=pop&limit=30&match_id={}&newest={}&order=desc&page_type=shop&version=2".format(
                    shopid,i*30)
                print(url)
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
        product_title = product_title.replace("'", "''")
        product_title = product_title.replace('"', '""')

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
            product['min_price'] = int(price_min_before_discount)/100000
        except Exception:
            pass

        try:
            price_max_before_discount = item['price_max_before_discount']
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
            brand = brand.replace("'", "''")
            brand = brand.replace('"', '""')
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
            display_name = display_name.replace("'", "''")
            display_name = display_name.replace('"', '""')
            product['cname1'] = display_name
        except Exception:
            pass

        try:
            product['cid2'] = item['categories'][1]['catid']
            display_name = item['categories'][1]['display_name']
            display_name = display_name.replace("'", "''")
            display_name = display_name.replace('"', '""')
            product['cname2'] = display_name
        except Exception:
            pass

        try:
            product['cid3'] = item['categories'][2]['catid']
            display_name = item['categories'][2]['display_name']
            display_name = display_name.replace("'", "''")
            display_name = display_name.replace('"', '""')
            product['cname3'] = display_name
        except Exception:
            pass

        description = item['description']
        description = description.replace("'", "''")
        description = description.replace('"', '""')
        product['description'] = description

        product['status'] = 1

        attributes = json.dumps(item['attributes'])
        attributes = attributes.replace("'", "''")
        attributes = attributes.replace('"', '""')
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
        print('goods异常--',e)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


# 商品数据变更处理
def product_change(product,item):
    product_change = trans_product_change(product)
    spu = product['spu']
    result = redis_db.hget("historical_product",spu)
    if result is not None:
        print('旧数据，比对')
        historical_product = json.loads(result)
        change = json_tools.diff(dict(product_change), historical_product)
        if len(change) == 0:
            # print('数据未变动,只需要改动shopee_product update_time')
            sql = "update shopee_product set update_time=%s ,status = 1 , update_by= %s where spu= %s"
            now_time = datetime.datetime.now()
            dbpool.Pool().update(sql,(now_time,'007',spu))
        else:
            # print('数据变动,更新shopee_product，并插入shopee_product_change一条变更后新数据')
            # status = 1 为了遇到曾经下架再次上架的商品，进行状态的改变
            sql = "update shopee_product set " \
                  "historical_sold=%s ," \
                  "price=%s ," \
                  "height_price=%s ," \
                  "product_title=%s ," \
                  " quantity=%s ," \
                  " status = 1 ," \
                  " update_time=%s ," \
                  " update_by= %s" \
                  " where spu= %s"
            params = (product['historical_sold'],
                      product['price'],
                      product['height_price'],
                      product['product_title'],
                      product['quantity'],
                      datetime.datetime.now(),
                      '007',
                      spu)
            dbpool.Pool().update(sql,params)
            dbpool.Pool().insert_temp('shopee_product_change', product,'shopee_product_change')
    else:
        # print('新数据，入库shopee_product,shopee_product_change,并同步到historical_shops')
        dbpool.Pool().insert_temp('shopee_product', product,'shopee_product')
        dbpool.Pool().insert_temp('shopee_product_change', product,'shopee_product_change')

    redis_db.hset('historical_product',spu,json.dumps(dict(product_change),cls = DateEnconding))

    # 子产品处理
    good_sub(item,product)


# 子商品
def good_sub(json_str,product):
    sub_list = []
    new_sub_list = []
    old_sub_list = []
    old_sub_change_list = []
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
                # print('数据未变动,只需要改动shopee_product update_time')
                now_time = datetime.datetime.now()
                old_sub_list.append((now_time,'007',spu,sku))
            else:
                # print('数据变动,更新 shopee_sub_product，并插入 shopee_sub_product_change 一条变更后新数据')
                # status = 1 为了遇到曾经下架再次上架的商品，进行状态的改变
                status = 1
                quantity = product['quantity']
                if quantity == 0:
                    status = 0
                params = (sub_product['sales_attributes'],
                          sub_product['price'],
                          sub_product['before_price'],
                          sub_product['sold'],
                          sub_product['quantity'],
                          status,
                          datetime.datetime.now(),
                          '007',
                          spu,
                          sku)
                old_sub_change_list.append(params)
                sub_list.append(sub_product)
        else:
            # print('新数据，入库 shopee_sub_product,shopee_sub_product_change,并同步到 historical_product_sub')
            sub_list.append(sub_product)
            new_sub_list.append(sub_product)
        redis_db.hset('historical_product_sub',key,json.dumps(dict(product_sub_change),cls = DateEnconding))

    sql = "update shopee_sub_product set update_time=%s , update_by= %s where spu= %s and sku = %s"
    dbpool.Pool().update_many(sql,'shopee_sub_product update time',old_sub_list)

    sql = "update shopee_sub_product set sales_attributes=%s ,price=%s ," \
          "before_price=%s ,sold=%s ,quantity=%s ,status = %s ,update_time=%s ,update_by= %s" \
          " where spu= %s and sku= %s"
    dbpool.Pool().update_many(sql,'shopee_sub_product update',old_sub_change_list)

    if len(new_sub_list) > 0:
        dbpool.Pool().insert_many_temp('shopee_sub_product', new_sub_list,'shopee_sub_product')

    if len(sub_list) > 0:
        dbpool.Pool().insert_many_temp('shopee_sub_product_change', sub_list,'shopee_sub_product_change')


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
        sub_product['price'] = int(price)/100000
    except Exception:
        pass
    try:
        price_before_discount = model['price_before_discount']
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
    product(task)


