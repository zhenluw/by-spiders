#! /bin/bash
# 最简洁的启动
nohup python3 /home/crawler/by-spiders/by/spiders/shopee/queue_to_pipline.py >pipline.log 2>&1 &
echo $!>pipprocess.pid
echo start success!
#sed -i 's/\r$//' app_master.sh