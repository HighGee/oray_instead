#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: HaiJi.Wang
"""
import sys
import os
import time
import argparse
from cause.myip import get_local_ip
from cause.log_handler import own_log
from cause.tencent_api_handler import update_record, getSubDomains

reload(sys)
sys.setdefaultencoding("utf8")

if __name__ == "__main__":
    # 腾讯云API TOKEN信息
    request_method = "POST"
    requet_host = "cns.api.qcloud.com"
    request_path = "/v2/index.php"
    # 获取命令行参数
    parsers = argparse.ArgumentParser()
    parsers.add_argument("--secret_id", type=str, help="腾讯云API SECRET ID")
    parsers.add_argument("--secret_key", type=str, help="腾讯云API SECRET KEY")
    parsers.add_argument("--root_domain", type=str, help="指定根域名")
    parsers.add_argument("--host", type=str, help="指定解析转发的子域名")
    parsers.add_argument("--receivers", type=str,
                         help="指定程序异常时的消息接收人,--receivers \"email1@example.com;email2@example1.com\"")
    parsers.add_argument("--logfile", type=str, help="日志文件名称，默认dns.log")
    FLAGS, unparsed = parsers.parse_known_args()

    SecretID = FLAGS.secret_id
    SecretKEY = FLAGS.secret_key
    ROOT_DOMAIN = FLAGS.root_domain
    RECEIVERS = FLAGS.receivers
    HOST = FLAGS.host
    log_file = FLAGS.logfile

    if log_file is None:
        log_file = "%s/log/dns.log" % os.path.abspath(os.path.dirname(__file__))
    else:
        log_file = "%s/log/{}" % os.path.abspath(os.path.dirname(__file__))

    log_instance = own_log("ORAY_INSTEAD", log_file)

    dst_hosts = [HOST]
    wait_interval = 1
    # 初始化检测 当前出口IP与云端IP异同
    now_ip = get_local_ip(log_instance, RECEIVERS=RECEIVERS)
    if now_ip["status"] == "ok":
        now_nsip = ""
        for record in \
                getSubDomains(ROOT_DOMAIN, SecretID, SecretKEY, log_instance, request_method, requet_host,
                              request_path)[
                    "data"]["records"]:
            for host in dst_hosts:
                if host == record["name"]:
                    now_nsip = record["value"]
                    if now_ip["ip"] != now_nsip:
                        res = update_record(ROOT_DOMAIN, record["id"], host, "A", now_ip["ip"], SecretID, SecretKEY,
                                            log_instance, request_method, requet_host, request_path)
                        if res["codeDesc"] == "Success":
                            log_instance.info("初始化 解析更新成功 新IP为:{}".format(now_ip["ip"]))
                            time.sleep(wait_interval)
                    else:
                        log_instance.info("初始化成功 当前IP为:{}".format(now_ip["ip"]))
                        time.sleep(wait_interval)
    else:
        if now_ip["msg"] == "exception":
            time.sleep(wait_interval)
        else:
            time.sleep(wait_interval)

    # 监控变化
    while True:
        new_ip = get_local_ip(log_instance, RECEIVERS=RECEIVERS)
        if new_ip["status"] == "ok":
            if now_ip["status"] == "ok" and new_ip["ip"] == now_ip["ip"]:
                time.sleep(wait_interval)
                log_instance.info("解析未更新 IP无变化")
            else:
                allSubDomains = getSubDomains(ROOT_DOMAIN, SecretID, SecretKEY, log_file, request_method, requet_host,
                                              request_path)
                for record in allSubDomains["data"]["records"]:
                    for host in dst_hosts:
                        if host == record["name"]:
                            res = update_record(ROOT_DOMAIN, record["id"], host, "A", new_ip["ip"], SecretID, SecretKEY,
                                                log_instance, request_method, requet_host, request_path)
                            if res["codeDesc"] == "Success":
                                now_ip["ip"] = new_ip["ip"]
                                now_ip["status"] = "ok"
                                log_instance.info("解析更新成功 新IP为:{}".format(new_ip["ip"]))
                time.sleep(wait_interval)
        else:
            if new_ip["status"] == "wrong" and new_ip["msg"] == "http_status":
                log_instance.info("获取外网异常-开始等待")
                time.sleep(wait_interval * 60)
                log_instance.info("获取外网异常-等待结束")
            else:
                time.sleep(wait_interval)
                log_instance.info("未知异常异常-直接重试")
