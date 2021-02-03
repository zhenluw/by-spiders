"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/2/1 15:27
"""
import datetime
import json
import threading
import traceback

import requests
import time

from by.pipline.redisclient import RedisClient
from by.pipline.redisqueue import RedisQueue
from by.pipline.template import trans_product, trans_task
from by.utils.tools import sleep_random_time1, sql_str_escape, DateEnconding
from by.pipline import dbpool
queue_shopee_search = RedisQueue('shopee_search', 'mz')
# queue_shopee = RedisQueue('shopee', 'mz')
# redis_db = RedisClient()


def get_html(url):
    sleep_random_time1()
    headers = {
        'referer': 'https://ph.xiapibuy.com/shop/283669838',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    }
    # return mayi.html_get(url, headers)
    return requests.get(url,headers=headers).text



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

        # product['sold'] = item['sold']
        # product['historical_sold'] = item['historical_sold']
        #
        # product['url'] = 'https://ph.xiapibuy.com/product/{}/{}'.format(shopid,itemid)
        # product['shop_url'] = 'https://ph.xiapibuy.com/shop/{}'.format(shopid)
        # product['spu'] = item['itemid']
        # product_title = item['name']
        # product_title = sql_str_escape(product_title)

        # product['product_title'] = product_title
        # product['score'] = item['item_rating']['rating_star']
        #
        # product['ratings'] = item['cmt_count']

        # try:
        #     price_min = item['price_min']
        #     product['price'] = int(price_min)/100000
        # except Exception:
        #     pass
        #
        # try:
        #     price_max = item['price_max']
        #     product['height_price'] = int(price_max)/100000
        # except Exception:
        #     pass
        #
        # try:
        #     price_min_before_discount = item['price_min_before_discount']
        #     if price_min_before_discount <= 0:
        #         price_min_before_discount = 0
        #
        #     product['min_price'] = int(price_min_before_discount)/100000
        # except Exception:
        #     pass
        #
        # try:
        #     price_max_before_discount = item['price_max_before_discount']
        #     if price_max_before_discount <= 0:
        #         price_max_before_discount = 0
        #     product['max_price'] = int(price_max_before_discount)/100000
        # except Exception:
        #     pass
        #
        # product['quantity'] = item['stock']
        #
        # product['shopid'] = item['shopid']
        #
        # try:
        #     for brands in item['attributes']:
        #         brand_name = brands['name']
        #         brand_value = brands['value']
        #         if 'Brand' in brand_name:
        #             brand = brand_value
        #     brand = sql_str_escape(brand)
        #     product['brand'] = brand
        # except Exception:
        #     pass
        #
        # cats = []
        # for categorie in item['categories']:
        #     catid = categorie['catid']
        #     display_name = categorie['display_name']
        #     cats.append({
        #         "catid":catid,
        #         "display_name":display_name
        #     })
        #
        # try:
        #     product['cid1'] = item['categories'][0]['catid']
        #     display_name = item['categories'][0]['display_name']
        #     display_name = sql_str_escape(display_name)
        #     product['cname1'] = display_name
        # except Exception:
        #     pass
        #
        # try:
        #     product['cid2'] = item['categories'][1]['catid']
        #     display_name = item['categories'][1]['display_name']
        #     display_name = sql_str_escape(display_name)
        #     product['cname2'] = display_name
        # except Exception:
        #     pass
        #
        # try:
        #     product['cid3'] = item['categories'][2]['catid']
        #     display_name = item['categories'][2]['display_name']
        #     display_name = sql_str_escape(display_name)
        #     product['cname3'] = display_name
        # except Exception:
        #     pass

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

        # product['status'] = 1

        # attributes = json.dumps(item['attributes'])
        # attributes = sql_str_escape(attributes)
        # product['specifications'] = attributes
        # product['currency'] = item['currency']
        #
        # product['shipping_from'] = item['shop_location']
        # # product['shipping_cost'] = ''
        #
        # product['create_time']= datetime.datetime.now()
        # product['create_by']= '007'

        # 商品数据变更处理
        # print(product)
        dbpool.Pool().insert_temp('shopee_product', product,'shopee_product')

    except Exception as e:
        traceback.print_exc()
        print('goods异常--',e,url)
        # queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


def shopee_product():
    while True:
        queue_result = queue_shopee_search.get_nowait()
        # print(queue_result)
        if queue_result is not None:
            result_f = json.loads(queue_result.decode())
            if isinstance(result_f,dict):
                task = trans_task(result_f)
                product(task)
            elif isinstance(result_f,list):
                for result_f2 in result_f:
                    if 'fastjson' not in result_f2:
                        task = trans_task(result_f2)
                        product(task)
            else:
                print(type(result_f))
        else:
            time.sleep(10)


if __name__ == '__main__':
    for i in range(10):
        t2 = threading.Thread(target = shopee_product)     # target是要执行的函数名（不是函数），args是函数对应的参数，以元组的形式存在
        t2.start()


