# 加入下面两行，requests请求不报错InsecureRequestWarning
import datetime
import traceback
import json
# 加入下面两行，requests请求不报错InsecureRequestWarning
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
from by.utils import mayi
from by.pipline.template import trans_shop, trans_task, trans_product, trans_sub_product
from by.utils.tools import DateEnconding, sleep_random_time1
from by.pipline import dbpool
queue_shopee = RedisQueue('shopee', 'mz')


def get_html(url):
    sleep_random_time1()
    headers = {
        'referer': 'https://ph.xiapibuy.com/shop/283669838',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    }
    return mayi.html_get(url, headers)


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
        shop['shopid']= json_str['shopid']
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
        abstract = json_str['description']
        shop['abstract'] = abstract.replace("'", "''")
        shop['response_time']= json_str['preparation_time']
        shop['create_time']= datetime.datetime.now()
        # shop['update_time']= datetime.datetime.now()
        shop['create_by']= '007'
        # shop['update_by']= '007'

        # userid = json_str['userid']
        # username = json_str['account']['username']

        dbpool.Pool().insert_temp('shopee_shope', shop,'shopee_shope')

        # 传入队列内开始遍历商铺所有商品
        new_task = trans_task(task)
        new_task['parse_type'] = 'goods_list'
        new_task['country'] = country
        new_task['level'] = 1
        queue_shopee.put(json.dumps(dict(new_task),cls = DateEnconding))

    except Exception as e:
        traceback.print_exc()
        print('shop异常--',e)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))
    print('存入jd_comment队列')


# 商品列表
def goods_list(task):
    shopid = task['shopid']
    try:
        level = task['level']
        if level ==1 :
            url = "https://ph.xiapibuy.com/api/v2/search_items/?by=pop&limit=30&match_id={}&newest=0&order=desc&page_type=shop&version=2".format(
                shopid)
            task['url'] = url
            total_count = goods_list_parse(task)

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
            goods_list_parse(task)

    except Exception as e:
        traceback.print_exc()
        print('goods_list异常--',e)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


# 商品表解析
def goods_list_parse(task):
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
            queue_shopee.put(json.dumps(dict(new_task),cls = DateEnconding))
        return total_count
    except Exception as e:
        traceback.print_exc()
        print('goods_list异常--',e)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


# 商品详情
def goods(task):
    itemid = task['spu']
    shopid = task['shopid']
    try:
        url = "https://ph.xiapibuy.com/api/v2/item/get?itemid={}&shopid={}".format(itemid, shopid)
        html = get_html(url)
        # print(html)

        product = trans_product(task)

        item = json.loads(html)['item']

        product['country'] = item['shop_location']
        product['spu'] = item['itemid']
        product_title = item['name']
        product_title = product_title.replace("'", "''")
        product_title = product_title.replace('"', '""')

        product['product_title'] = product_title
        product['score'] = item['item_rating']['rating_star']

        product['ratings'] = item['cmt_count']
        product['sold'] = item['historical_sold']
        product['price'] = item['price_min']
        product['height_price'] = item['price_max']
        product['quantity'] = item['stock']

        product['shopid'] = item['shopid']

        for brands in item['attributes']:
            brand_name = brands['name']
            brand_value = brands['value']
            if 'Brand' in brand_name:
                brand = brand_value

        product['brand'] = brand.replace("'", "''")

        category = ''
        categorys = item['categories']
        for i in range(0,len(categorys)-1):
            display_name = categorys[i]['display_name']
            category += display_name+'>'
        category = category+categorys[len(categorys)-1]['display_name']
        product['category'] = category.replace("'", "''")

        description = item['description']
        description.replace("'", "''")
        description.replace('"', '""')
        product['description'] = description

        product['webid'] = 0
        product['status'] = 0
        product['login_user'] = ''
        product['specifications'] = ''
        product['create_time']= datetime.datetime.now()
        # product['update_time']= datetime.datetime.now()
        product['create_by']= '007'
        # product['update_by']= '007'


        dbpool.Pool().insert_temp('shopee_product', product,'shopee_product')

        good_sub(item,task)

    except Exception as e:
        traceback.print_exc()
        print('goods异常--',e)
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


# 子商品
def good_sub(json_str,task):
    lists = []
    for model in json_str['models']:
        sub_product = trans_sub_product(task)
        sub_product['spu'] = model['itemid']
        sub_product['sku'] = model['modelid']
        sub_product['status'] = model['status']
        sub_product['price'] = model['price']
        sub_product['quantity'] = model['stock']
        sub_product['sales_attributes'] = model['name']
        sub_product['create_time']= datetime.datetime.now()
        # sub_product['update_time']= datetime.datetime.now()
        sub_product['create_by']= '007'
        # sub_product['update_by']= '007'
        lists.append(sub_product)

    if len(lists) == 0:
        return
    dbpool.Pool().insert_many_temp('shopee_sub_product', lists,'shopee_sub_product')



if __name__ == '__main__':
    task={
        "shopid":'283669838',
        "parse_type":"shop",
        "level": 1,
    }
    # queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))
    # shop(task)

    task={"shopid": "283669838", "parse_type": "goods_list", "level": 1, "country": "PH"}
    # goods_list(task)

    task={"shopid": "283669838", "parse_type": "goods", "level": 1, "country": "PH", "url": "https://ph.xiapibuy.com/api/v2/search_items/?by=pop&limit=30&match_id=283669838&newest=0&order=desc&page_type=shop&version=2", "spu": 4952667936}
    goods(task)


