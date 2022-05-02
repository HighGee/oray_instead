#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: HaiJi.Wang
"""
import time
from utils.myip import get_local_ip
from utils.log_handler import own_log
from utils.tencent_api_handler import TencentCloudAPI
from settings import (
    INTERVAL,
    DNS_DOMAIN,
    DNS_HOST
)

LOGGER = own_log("SYNC")
NOW_IP = None


def sync_tx(now_ip):
    """检查当前IP与解析IP是否相同，不同则更新"""
    # 获取NS解析
    txCloud = TencentCloudAPI()
    tx_ret = txCloud.getSubDomains(DNS_DOMAIN)
    if not tx_ret:
        return False, '访问腾讯云接口异常'
    host_rds = [h for h in tx_ret["data"]["records"] if h["name"] == DNS_HOST]
    # 维护解析
    for host_rd in host_rds:
        now_nsip = host_rd["value"]
        if now_ip == now_nsip:
            return True, 'equal'
        tx_ret = txCloud.updateRecord(
            DNS_DOMAIN, host_rd["id"], DNS_HOST, "A", now_ip)
        if not tx_ret:
            return False, '访问腾讯云接口异常'
        if tx_ret["codeDesc"] == "Success":
            return True, 'update'


def sync_ns():
    global NOW_IP
    intvs = {
        "http_status": 60,
        "timeout": 20,
        "exception": 20,
    }
    # 获取当前出口
    ok, now_ip, msg = get_local_ip()
    if not ok:
        return intvs.get(msg)
    # 初始化
    if not NOW_IP:
        ok, msg = sync_tx(now_ip)
        if not ok:
            LOGGER.error(msg)
            return
        NOW_IP = now_ip
        LOGGER.info('初始化IP为：%s' % now_ip if msg ==
                    'equal' else '初始化更新IP为：%s' % now_ip)
        return
    # 常规同步
    if now_ip != NOW_IP:
        ok, msg = sync_tx(now_ip)
        if not ok:
            LOGGER.error(msg)
            return
        NOW_IP = now_ip
        LOGGER.info('出口变化更新当前IP为：%s' % now_ip)
        return
    LOGGER.info('出口未变化')
    return


if __name__ == "__main__":
    while True:
        time.sleep(sync_ns() or INTERVAL)
