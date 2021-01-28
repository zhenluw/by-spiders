"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/27 16:43
 
"""
import json
import requests
import sys
import os

from by.pipline.redisclient import RedisClient
from by.pipline.redisqueue import RedisQueue
from by.utils.tools import DateEnconding

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.pipline import dbpool
db = dbpool.Pool()
queue_shopee_search = RedisQueue('shopee_search', 'mz')
queue_shopee = RedisQueue('shopee', 'mz')
redis_db = RedisClient(11)


if __name__ == '__main__':
    shopids = redis_db.hgetall("shops")
    for shopid in shopids:
        print(shopid)
        task = {
            "shopid":shopid,
            "parse_type":"shop",
            "webid":1,
            "level": 1,
            "country": "PH",
        }
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))
        break



