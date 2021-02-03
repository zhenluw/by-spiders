#! /bin/bash
# 最简洁的启动
nohup python3 /home/crawler/by-spiders/by/spiders/shopee/app_master.py >spider.log 2>&1 &
echo $!>appprocess.pid
echo start success!
#sed -i 's/\r$//' app_master.sh