"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/28 12:53
 
"""
# import json_tools
# src = {'numbers': [1, 3, 4, 8], 'foo': 'bar'}
# dst = {'numbers': [1, 3, 4, 8,8], 'foo': 'bar6'}
# patch = json_tools.diff(src, dst)
# print(patch)
# print(len(patch))

from by.pipline.redisclient import RedisClient
from by.pipline.redisqueue import RedisQueue
from by.pipline.template import trans_search, trans_task
from by.utils.tools import DateEnconding, sleep_random_time1
from by.pipline import dbpool
queue_shopee_search = RedisQueue('shopee_search', 'mz')
queue_shopee = RedisQueue('shopee', 'mz')
# redis_db = RedisClient()
cache_shop = RedisQueue('cache_shop', 'mz')
cache_product = RedisQueue('cache_product', 'mz')
cache_product_sub = RedisQueue('cache_product_sub', 'mz')

# result = dbpool.Pool().get_all("select distinct(shopid) from shopee_search")
# for item in result:
#     print(item['shopid'])
#     redis_db.hset('shops',item['shopid'],0)

for i in range(1000):
    cache_product_sub.put(i)