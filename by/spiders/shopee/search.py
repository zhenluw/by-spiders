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
from by.pipline.redisclient import RedisClient
from by.pipline.redisqueue import RedisQueue
from by.pipline.template import trans_search, trans_task
from by.utils.tools import DateEnconding, sleep_random_time1
from by.pipline import dbpool
queue_shopee_search = RedisQueue('shopee_search', 'mz')
queue_shopee = RedisQueue('shopee', 'mz')
redis_db = RedisClient(11)

def get_html(url):
    sleep_random_time1()
    headers = {
        'referer': 'https://ph.xiapibuy.com/search?keyword=anime%20cartoon%20printed%20short%20sleeve&page=5&sortBy=ctime',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'x-api-source':'pc',
        'x-shopee-language':'en',
    }

    # return mayi.html_get(url, headers)
    return requests.get(url,headers=headers).text


# 商铺详情
def search(task):
    print(task)
    sort = task['sort']
    keyword = task['keyword']
    page = task['page']
    try:
        # url = "https://ph.xiapibuy.com/api/v2/search_items/?by={}&keyword={}&limit=50&newest=0&order=desc&page_type=search&version=2".format(sort,keyword)
        url = "https://ph.xiapibuy.com/api/v2/search_items/?by={}&keyword={}&limit=50&locations=-2&newest=0&order=desc&page_type=search&skip_autocorrect=1&version=2".format(sort,keyword)
        print(url)
        html = get_html(url)
        print(html)
        json_str = json.loads(html)

        search_list = []
        num = 1
        for item in json_str['items']:
            search = trans_search(task)
            search['position'] = '{}-{}'.format(page,num)

            shopid = item['shopid']
            search['shopid']= shopid
            search['create_time']= datetime.datetime.now()
            # search['update_time']= datetime.datetime.now()
            search['spu']= item['itemid']
            search['historical_sold']= item['historical_sold']
            search['sold']= item['sold']
            search['shipping_from']= item['shop_location']
            search['ad'] = item['adsid']
            try:
                adsid = item['adsid']
                if adsid is not None:
                    search['ad']= 1
                else:
                    search['ad']= 0
            except Exception:
                search['ad']= 0
            num += 1
            search_list.append(search)

            redis_db.hset('shops',shopid,0)
            # redis_db.set(shopid,json.dumps(dict(new_task),cls = DateEnconding))

        dbpool.Pool().insert_many_temp('shopee_search', search_list,'shopee_search')

    except Exception as e:
        traceback.print_exc()
        print('search异常--',e)
        queue_shopee_search.put(json.dumps(dict(task),cls = DateEnconding))
    print('存入redis队列')




if __name__ == '__main__':
    task = {
        "sort":'sales',
        "keyword":"dress",
        "webid":1,
        "parse_type": "search",
        "country": "PH",
        "page": 1,
    }
    # queue_shopee_search.put(json.dumps(dict(task),cls = DateEnconding))
    search(task)

    # shopids = redis_db.hgetall("shops")
    # for shopid in shopids:
    #     # print(shopid)
    #     task = {
    #         "shopid":shopid,
    #         "parse_type":"shop",
    #         "webid":1,
    #         "level": 1,
    #         "country": "PH",
    #     }
    #     queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))

    # shopids = redis_db.hget("shops",'41311013')
    # print(shopids)


