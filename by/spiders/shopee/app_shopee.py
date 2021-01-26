"""
 * @Project_Name: lav-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2020/9/17 17:11
"""
import json
import os
import sys
import threading
import time
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.spiders.shopee.search_master import shop, goods_list,goods
from by.pipline.redisqueue import RedisQueue
from by.pipline.template import trans_task

queue_shopee = RedisQueue('shopee', 'mz')


def deal(task):
    parse_type = task['parse_type']
    if parse_type == 'shop':
        shop(task)
    if parse_type == 'goods_list':
        goods_list(task)
    if parse_type == 'goods':
        goods(task)



def shopee():
    while True:
        queue_result = queue_shopee.get_nowait()
        if queue_result is not None:
            result_f = json.loads(queue_result)
            if isinstance(result_f,dict):
                task = trans_task(result_f)
                deal(task)
            elif isinstance(result_f,list):
                for result_f2 in result_f:
                    if 'fastjson' not in result_f2:
                        task = trans_task(result_f2)
                        deal(task)
            else:
                print(type(result_f))
        else:
            time.sleep(10)



if __name__ == '__main__':
    for i in range(10):
        t2 = threading.Thread(target = shopee)     # target是要执行的函数名（不是函数），args是函数对应的参数，以元组的形式存在
        t2.start()
