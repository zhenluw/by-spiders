#!/bin/bash

# 最简洁的启动

nohup python3  app_master.py > spider.log 2>&1 &

echo $!>process.pid

echo start success!