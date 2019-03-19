# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:32
import requests
import json
from cause.email_handler import mail_mass
from cause.log_handler import own_log
from cause.config import own_cfg

ip_logger = own_log("GET_IP", own_cfg.log_file)

"""
出口IP获取模块
"""


def get_ip(ip_url, receivers):
    result = {"status": "wrong"}
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0"}
    try:
        rep = requests.get(ip_url, headers=headers, timeout=5)
        if rep.status_code != 200:
            ip_logger.error(u"站点{}访问异常，无法获取出口IP，状态码为 {}".format(ip_url, rep.status_code))
            ban_codes = [403, 521, 555]
            err_codes = [404, 502, 504]
            if rep.status_code in ban_codes:
                ban_title = u"[拦截]出口IP获取异常，状态码为{}".format(rep.status_code)
            elif rep.status_code in err_codes:
                ban_title = u"[故障]出口IP获取异常，状态码为{}".format(rep.status_code)
            else:
                ban_title = u"[未知]出口IP获取异常，状态码为{}".format(rep.status_code)
            mail_mass(receivers, title=ban_title)
            result["msg"] = "http_status"
        else:
            my_ip = json.loads(rep.content)["client_ip"]
            result.update({"status": "ok", "ip": my_ip})
    except Exception, e:
        ip_logger.error(u"当前网络异常，无法获取出口IP，{}".format(e))
        mail_mass(receivers)
        result["msg"] = "exception"

    return result


def get_local_ip(receivers=None):
    ip_urls = ["http://ip.haiji.pro", "http://ip.haiji.io"]
    ip_res = get_ip(ip_urls[0], receivers)
    if ip_res["status"] == "wrong":
        ip_res = get_ip(ip_urls[1], receivers)
    return ip_res
