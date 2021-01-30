"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/27 16:43
 
"""
import json
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.pipline import dbpool
from by.pipline.redisclient import RedisClient
from by.pipline.redisqueue import RedisQueue
from by.utils.tools import DateEnconding

db = dbpool.Pool()
queue_shopee_search = RedisQueue('shopee_search', 'mz')
queue_shopee = RedisQueue('shopee', 'mz')
redis_db = RedisClient()


# 重新同步mysql 和redis shop
def update_shop_to_redis():
    result = db.get_all("select distinct(shopid) from shopee_search ")
    for item in result:
        shopid = item['shopid']
        redis_db.hset('shops',shopid,0)


# 将搜索词推送到search搜索任务队列中
def push_search():
    result = db.get_all("select * from search_keyword where status is null")
    for item in result:
        keyword = item['keyword']
        page = item['page']
        for i in range(1,page+1):
            task = {
                "sort":'sales',
                "keyword":keyword,
                "webid":1,
                "parse_type": "search",
                "country": "PH",
                "page": i,
            }
            print(task)
            queue_shopee_search.put(json.dumps(dict(task),cls = DateEnconding))


# 将redis中shops库的所有数据推送到shop采集任务队列中
def push_shop():
    shopids = redis_db.hgetall("shops")
    for shopid in shopids:
        task = {
            "shopid":shopid,
            "parse_type":"shop",
            "webid":1,
            "level": 1,
            "country": "PH",
        }
        print(task)
        if '306258110' in shopid:
            continue
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))

        # break


if __name__ == '__main__':
    push_search()
    # push_shop()
    # update_shop_to_redis()



