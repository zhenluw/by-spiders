"""
 * @Project_Name: lav-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2020/9/12 14:32
 
"""
import json
import requests
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.pipline import dbpool
db = dbpool.Pool()


def push_key_to_redis(queue,keyword,cid,eid):
    data = {
        "queue":queue,
            "value":{
        "title":cid,
                     "keyword":'魅可妆前底唇膏',
                 "project_name":"白皮书20201203",
                "url":keyword,
                 "parse_level":"tmall_search",
                "channel":"tmall",
                "level": 1,
                 "cid": cid,
                 "eid": eid,
                "price": eid,
                 "page": 10,
                 "start_time": "2020-05-01",
                 "end_time": "2020-12-01",
                 }
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post("http://52.83.45.179:9085/api/redis/QueuePut", headers=headers, data=json.dumps(data))
    # response = requests.post("http://localhost:9085/api/redis/QueuePut", headers=headers, data=json.dumps(data))
    html = response.text
    print(html)


def select_start_id(table_name,queue):
    # sql = "select id,cid,name,eid from {} where status is null ".format(table_name)
    sql = "select id,cid,name,eid from {} limit 1 ".format(table_name)
    # sql = "select * from template where link not in (select url from template_jd_info)"
    results = db.get_all2(sql)
    for result in results:
        print(result)
        # id = result['link']
        keyword = result['name']
        # cid = result['price']
        # eid = result['eid']
        push_key_to_redis(queue,'','','')
        # update_sql = "update {} set status = 0 where id={} ".format(table_name,id)
        # db.update(update_sql)


if __name__ == '__main__':
    table_name = 'shop_list_copy1'
    queue = 'tmall:mz'
    select_start_id(table_name,queue)


