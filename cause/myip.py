# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:32
import requests
import json
from .email import mail_mass

"""
出口IP获取模块
"""


def get_local_ip(log_instance, RECEIVERS=None):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0"}
    result = {"status": "wrong"}
    try:
        ip_url = "https://haiji.io/get_way_out.php"
        rep = requests.get(ip_url, headers=headers, timeout=5)
        if rep.status_code != 200:
            log_instance.error(u"站点访问异常，无法获取出口IP，状态码为 {}".format(rep.status_code))
            ban_codes = [403, 521, 555]
            err_codes = [404, 502, 504]
            if rep.status_code in ban_codes:
                ban_title = u"[拦截]出口IP获取异常，状态码为{}".format(rep.status_code)
            elif rep.status_code in err_codes:
                ban_title = u"[故障]出口IP获取异常，状态码为{}".format(rep.status_code)
            else:
                ban_title = u"[未知]出口IP获取异常，状态码为{}".format(rep.status_code)
            mail_mass(RECEIVERS, log_instance, title=ban_title)
            result["msg"] = "http_status"
        else:
            my_ip = json.loads(rep.content)["client_ip"]
            result.update({"status": "ok", "ip": my_ip})
    except Exception, e:
        log_instance.error(u"当前网络异常，无法获取出口IP，{}".format(e))
        mail_mass(RECEIVERS, log_instance)
        result["msg"] = "exception"
    return result
