"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/27 16:43
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
from by.spiders.shopee.search import search
from by.spiders.shopee.shop import shop, product_list, product
from by.pipline.redisqueue import RedisQueue
from by.pipline.template import trans_task

queue_shopee = RedisQueue('shopee', 'mz')
queue_shopee_search = RedisQueue('shopee_search', 'mz')


def deal(task):
    parse_type = task['parse_type']
    if parse_type == 'search':
        search(task)
    if parse_type == 'shop':
        shop(task)
        print()
    if parse_type == 'goods_list':
        product_list(task)
    if parse_type == 'goods':
        product(task)


def shopee():
    while True:
        queue_result = queue_shopee.get_nowait()
        # print(queue_result)
        if queue_result is not None:
            result_f = json.loads(queue_result.decode())
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


def shopee_search():
    while True:
        queue_result = queue_shopee_search.get_nowait()
        # print(queue_result)
        if queue_result is not None:
            result_f = json.loads(queue_result.decode())
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
    # for i in range(1):
    #     t2 = threading.Thread(target = shopee)     # target是要执行的函数名（不是函数），args是函数对应的参数，以元组的形式存在
    #     t2.start()
    for i in range(3):
        t2 = threading.Thread(target = shopee_search)     # target是要执行的函数名（不是函数），args是函数对应的参数，以元组的形式存在
        t2.start()

