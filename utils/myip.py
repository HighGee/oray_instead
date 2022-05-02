# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:32
import json
import requests
from utils.email_handler import mail_mass
from utils.log_handler import own_log
from utils.dns_query import DNSQuery
from settings import (
    HTTP_BAN_CODES,
    HTTP_ERR_CODES
)

LOGGER = own_log("GET_IP")

"""
出口IP获取模块
"""


def get_ip(ip_host):
    result = {"status": "wrong"}
    dst_ip = DNSQuery(ip_host)["ips"][0]
    headers = {
        "Host": ip_host,
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",  # noqa
    }
    try:
        rep = requests.get("http://{}?type=json".format(dst_ip),
                           headers=headers, timeout=5)
        if rep.status_code != 200:
            LOGGER.error(u"站点{}访问异常，无法获取出口IP，状态码为 {}".format(
                ip_host, rep.status_code))
            title = u"[未知]出口IP获取异常，状态码为 {}".format(rep.status_code)
            if rep.status_code in HTTP_BAN_CODES + HTTP_ERR_CODES:
                title = u"[拦截]出口IP获取异常，状态码为 {}".format(rep.status_code)
            content = "站点 {} 响应出现异常，尽快修复;".format(ip_host)
            mail_mass(title=title, content=content)
            result["msg"] = "http_status"
            return result
        my_ip = json.loads(rep.content)["client"]
        result.update({"status": "ok", "ip": my_ip})
    except TimeoutError:
        LOGGER.error(u"请求超时，无法获取出口IP")
        result["msg"] = "timeout"
    except Exception as e:
        LOGGER.error(u"当前网络异常，无法获取出口IP，{}".format(e))
        result["msg"] = "exception"

    return result


def get_local_ip():
    dms = ["ip.haiji.pro", "ip.haiji.io"]
    ip_res = get_ip(dms[0])
    if ip_res["status"] == "ok":
        return True, ip_res['ip'], ''
    ip_res = get_ip(dms[1])
    if ip_res["status"] == "wrong":
        mail_mass()
        return False, '', ip_res['msg']
    return True, ip_res['ip'], ''
