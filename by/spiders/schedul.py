"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/27 16:43
"""
import datetime
import json
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.pipline.redisqueue import RedisQueue
from apscheduler.schedulers.blocking import BlockingScheduler
from by.utils.tools import DateEnconding
from by.pipline.redisclient import RedisClient

queue_shopee_search = RedisQueue('shopee_search', 'mz')
queue_shopee = RedisQueue('shopee', 'mz')

redis_db = RedisClient(11)

scheduler = BlockingScheduler()   # 后台运行

# 设置为每日凌晨00:1:1时执行一次调度程序
@scheduler.scheduled_job("cron", day_of_week='*', hour='1', minute='1', second='1')
# @scheduler.scheduled_job("cron", day_of_week='*', hour='*', minute='*', second='3')
def search():
    """
    关键词dress每日搜索第一页task push到redis，然后search爬虫会进行采集
    :return:
    """
    print("search-------" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    task = {
        "sort":'sales',
        "keyword":"dress",
        "webid":1,
        "parse_type": "search",
        "country": "PH",
        "page": 1,
    }
    queue_shopee_search.put(json.dumps(dict(task),cls = DateEnconding))


@scheduler.scheduled_job("cron", day_of_week='*', hour='1', minute='30', second='1')
# @scheduler.scheduled_job("cron", day_of_week='*', hour='*', minute='*', second='4')
def shop():
    """
    遍历shops（新增+历史shopid），创建成task push到redis，交给shop进行采集
    :return:
    """
    print("shop------" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    shopids = redis_db.hgetall("shops")
    for shopid in shopids:
        # print(shopid)
        task = {
            "shopid":shopid,
            "parse_type":"shop",
            "webid":1,
            "level": 1,
            "country": "PH",
        }
        queue_shopee.put(json.dumps(dict(task),cls = DateEnconding))


if __name__ == '__main__':
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("statistic scheduler start-up fail")