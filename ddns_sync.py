#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: HaiJi.Wang
"""
import time
import argparse
from cause.myip import get_local_ip
from cause.log_handler import own_log
from cause.tencent_api_handler import update_record, getSubDomains
from cause.config import own_cfg


if __name__ == "__main__":
    requet_host = own_cfg.REQUEST["host"]
    request_path = own_cfg.REQUEST["path"]
    request_method = own_cfg.REQUEST["method"]

    ROOT_DOMAIN = own_cfg.DNS_DOMAIN
    HOST = own_cfg.DNS_HOST

    main_logger = own_log("SYNC")

    dst_hosts = [HOST]
    wait_interval = 1
    # 初始化检测 当前出口IP与云端IP异同
    now_ip = get_local_ip()
    if now_ip["status"] == "ok":
         now_nsip = ""
         for record in getSubDomains(ROOT_DOMAIN)["data"]["records"]:
             for host in dst_hosts:
                 if host == record["name"]:
                     now_nsip = record["value"]
                     if now_ip["ip"] != now_nsip:
                         res = update_record(
                             ROOT_DOMAIN, record["id"], host, "A", now_ip["ip"])
                         if res["codeDesc"] == "Success":
                             main_logger.info(
                                 "初始化 解析更新成功 新IP为:{}".format(now_ip["ip"]))
                             time.sleep(wait_interval)
                     else:
                         main_logger.info(
                             "初始化成功 当前IP为:{}".format(now_ip["ip"]))
                         time.sleep(wait_interval)
    else:
        if now_ip["msg"] == "exception":
            time.sleep(wait_interval)
        else:
            time.sleep(wait_interval)

    # 监控变化
    while True:
        new_ip = get_local_ip()
        if new_ip["status"] == "ok":
            if now_ip["status"] == "ok" and new_ip["ip"] == now_ip["ip"]:
                time.sleep(wait_interval)
                main_logger.info("解析未更新 IP无变化")
            else:
                allSubDomains = getSubDomains(ROOT_DOMAIN)
                for record in allSubDomains["data"]["records"]:
                    for host in dst_hosts:
                        if host == record["name"]:
                            res = update_record(
                                ROOT_DOMAIN, record["id"], host, "A", new_ip["ip"])
                            if res["codeDesc"] == "Success":
                                now_ip["ip"] = new_ip["ip"]
                                now_ip["status"] = "ok"
                                main_logger.info(
                                    "解析更新成功 新IP为:{}".format(new_ip["ip"]))
                time.sleep(wait_interval)
        else:
            if new_ip["status"] == "wrong" and new_ip["msg"] == "http_status":
                main_logger.info("获取外网异常-开始等待")
                time.sleep(wait_interval * 60)
                main_logger.info("获取外网异常-等待结束")
            else:
                time.sleep(wait_interval)
                main_logger.info("未知异常异常-直接重试")
