"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/27 16:43
"""
import datetime
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.pipline.redisqueue import RedisQueue
from apscheduler.schedulers.blocking import BlockingScheduler
from by.spiders.shopee.push_keys import push_search, push_shop
from by.pipline.redisclient import RedisClient

queue_shopee_search = RedisQueue('shopee_search', 'mz')
queue_shopee = RedisQueue('shopee', 'mz')
redis_db = RedisClient()

scheduler = BlockingScheduler()   # 后台运行

# 设置为每日凌晨00:1:1时执行一次调度程序
@scheduler.scheduled_job("cron", day_of_week='*', hour='11', minute='55', second='1')
# @scheduler.scheduled_job("cron", day_of_week='*', hour='*', minute='*', second='3')
def search():
    """
    关键词dress每日搜索第一页task push到redis，然后search爬虫会进行采集
    :return:
    """
    print("search-------" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    push_search()


@scheduler.scheduled_job("cron", day_of_week='*', hour='11', minute='55', second='1')
# @scheduler.scheduled_job("cron", day_of_week='*', hour='*', minute='*', second='4')
def shop():
    """
    遍历shops（新增+历史shopid），创建成task push到redis，交给shop进行采集
    :return:
    """
    print("shop------" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    push_shop()


if __name__ == '__main__':
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("statistic scheduler start-up fail")