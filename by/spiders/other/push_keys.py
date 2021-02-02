"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/2/1 15:27
"""
import datetime
import json
import threading
import traceback

import requests
import time

from by.pipline.redisclient import RedisClient
from by.pipline.redisqueue import RedisQueue
from by.pipline.template import trans_product, trans_task
from by.utils.tools import sleep_random_time1, sql_str_escape, DateEnconding
from by.pipline import dbpool
queue_shopee_search = RedisQueue('shopee_search', 'mz')
# queue_shopee = RedisQueue('shopee', 'mz')
# redis_db = RedisClient()
cache_product_update = RedisQueue('cache_product_update', 'mz')


def push_search():
    pool = dbpool.Pool()
    result = dbpool.Pool().get_all("select * from shopee_product_copy1 where create_by is null ")
    for item in result:
        shopid = item['shopid']
        spu = item['spu']
        task= {
            "shopid": shopid,
            "webid": 1,
            "country": "PH",
            "parse_type": "goods",
            "level": 1,
            "spu": spu
        }
        print(task)
        queue_shopee_search.put(json.dumps(dict(task),cls = DateEnconding))
        # product(task)
        sql = "update shopee_product_copy1 set create_by=1 where shopid='{}' and spu='{}'".format(shopid,spu)
        print(sql)
        pool.update(sql)
        # time.sleep(5)


if __name__ == '__main__':
    push_search()
    data_list0=[]
    for i in range(1000):
        product = {
            "historical_sold":3089,
            "price":239,
            "height_price":239,
            "product_title":"Men''s Oversize Loose Big Size Short Sleeved T shirt Summer Korean Style Fashion Letter Printied T Shirt For Men Unisex Cotton Round Neck T Shirt Tees Student Versatile Breathable Bottoming Shirt Couple Streetwear Tees Tops",
            "quantity":17728,
            "spu":'7543532138',
        }
        data_list0.append(product)

    # a= datetime.datetime.now()
    # dbpool.Pool().insert_many_temp('shopee_product', data_list0,'shopee_product')
    # b= datetime.datetime.now()
    # print(b-a)
    #


    sql = "update shopee_product set " \
          "historical_sold=%s ," \
          "price=%s ," \
          "height_price=%s ," \
          "product_title=%s ," \
          " quantity=%s ," \
          " status = 1 ," \
          " update_by= %s" \
          " where spu= %s"

    # sql = "update shopee_product set " \
    #       "historical_sold=(%s) ," \
    #       "price=(%s) ," \
    #       "height_price=(%s) ," \
    #       "product_title=(%s) ," \
    #       " quantity=(%s) ," \
    #       " status = 1 ," \
    #       " update_time=(%s) ," \
    #       " update_by= (%s)" \
    #       " where spu= (%s)"

    data_list3=[]
    for i in range(100):
        params = (3089,
                  239,
                  239,
                  "Men''s Oversbgf4275412b0158541ize Lo0ose Big Size S010ho0rt Sleeved T shirt Summer Korean Style Fashion Letter Printied T Shirt For Men Unisex Cotton Round Neck T Shirt Tees Student Versatile Breathable Bottoming Shirt Couple Streetwear Tees Tops",
                  17728,
                  '007',
                  7543532138)
        data_list3.append(params)

    # a= datetime.datetime.now()
    # dbpool.Pool().update_many(sql,'shopee_product update time',data_list3)
    # b= datetime.datetime.now()
    # print(b-a)
    # 0:00:04.369308
