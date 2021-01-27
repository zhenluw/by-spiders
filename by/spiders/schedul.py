"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/27 16:43
"""
import datetime
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.pipline.redisqueue import RedisQueue
from by.utils.tools import DateEnconding

queue_shopee_search = RedisQueue('shopee_search', 'mz')

scheduler = BlockingScheduler()   # 后台运行

# 设置为每日凌晨00:30:30时执行一次调度程序
# @scheduler.scheduled_job("cron", day_of_week='*', hour='1', minute='30', second='30')
@scheduler.scheduled_job("cron", day_of_week='*', hour='*', minute='*', second='3')
def search():
    print("search-------" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    task = {
        "sort":'sales',
        "keyword":"dress",
        "webid":1,
        "parse_type": "search",
        "country": "PH",
        "page": 1,
    }
    # queue_shopee_search.put(json.dumps(dict(task),cls = DateEnconding))


@scheduler.scheduled_job("cron", day_of_week='*', hour='*', minute='*', second='4')
def shop():
    print("shop------" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # task = {
    #     "sort":'sales',
    #     "keyword":"dress",
    #     "webid":1,
    #     "parse_type": "search",
    #     "country": "PH",
    #     "page": 1,
    # }
    # queue_shopee_search.put(json.dumps(dict(task),cls = DateEnconding))


if __name__ == '__main__':
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("statistic scheduler start-up fail")