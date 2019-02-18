#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: HaiJi.Wang
"""
import sys
import urllib
import os
import httplib
import binascii
import hashlib
import requests
import hmac
import time
import random
import json
import re
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler
import smtplib
from email.mime.text import MIMEText
from email.header import Header

reload(sys)
sys.setdefaultencoding("utf8")

# 腾讯云API TOKEN信息
requestMethod = "POST"
requestHost = "cns.api.qcloud.com"
requestPath = "/v2/index.php"

# 出口获取地址
ownSrvUrl = "https://haiji.io/get_way_out.php"
ipipNetUrl = "http://myip.ipip.net"


class IsMail():
    """
    判断是否为邮箱地址
    """

    def __init__(self):
        self.p = re.compile(r"[^\._][\w\._-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$")

    def ismail(self, str):
        res = self.p.match(str)
        if res:
            return True
        else:
            return False


def appLog(app_name, log_file):
    """
    日志模块
    """
    log_instance = logging.getLogger(app_name)
    log_instance.setLevel(logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter("%(asctime)s %(name)s %(filename)s %(levelname)s %(message)s")
    formatter.datefmt = "%Y-%m-%d %H:%M:%S"

    file_handler = TimedRotatingFileHandler(log_file, when='H', backupCount=15 * 24)
    file_handler.setFormatter(formatter)
    log_instance.addHandler(file_handler)

    return log_instance


def send_errmsg(receiver, log_instance, title=None, content=None):
    """
    邮件通知模块
    """
    is_email = IsMail()
    if is_email.ismail(receiver[0]):
        if title is None:
            title = u"[故障]出口IP获取异常"
        if content is None:
            content = requests.get(ipipNetUrl).content
        msg = MIMEText(content, "html", _charset="utf-8")
        me = "OrayInstead@haiji.io"
        msg["Subject"] = Header(title, charset="utf-8")
        msg["From"] = me
        msg["To"] = ";".join(receiver)

        s = smtplib.SMTP("localhost")
        s.sendmail(me, receiver, msg.as_string())
        s.quit()
    else:
        log_instance.error(u"邮件通知失败，目标邮箱：%s" % ";".join(receiver))


def mail_mass(receivers, title=None, content=None):
    if receivers is not None:
        if ";" in receivers:
            for email in receivers.split(";"):
                send_errmsg([email], title=title, content=content)
        else:
            send_errmsg([receivers], title=title, content=content)


"""
出口IP获取模块
"""


def get_local_ip(log_instance, RECEIVERS=None):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0"}
    try:
        rep = requests.get(ownSrvUrl, headers=headers)
        if rep.status_code != 200:
            log_instance.error(u"站点访问异常，无法获取出口IP，状态码为 {}".format(rep.status_code))
            result = {"status": "wrong", "msg": "http_status"}
            ban_codes = [403, 521, 555]
            err_codes = [404, 502, 504]
            if rep.status_code in ban_codes:
                ban_title = u"[拦截]出口IP获取异常，状态码为{}".format(rep.status_code)
            elif rep.status_code in err_codes:
                ban_title = u"[故障]出口IP获取异常，状态码为{}".format(rep.status_code)
            else:
                ban_title = u"[未知]出口IP获取异常，状态码为{}".format(rep.status_code)

            mail_mass(RECEIVERS, ban_title)
        else:
            my_ip = json.loads(rep.content)["client_ip"]
            result = {"status": "ok", "ip": my_ip}
    except Exception, e:
        log_instance.error(u"当前网络异常，无法获取出口IP，{}".format(e))
        mail_mass(RECEIVERS)
        result = {"status": "wrong", "msg": "exception"}
    return result


"""
腾讯云API 相关
"""


def makePlainText(requestMethod, requestHost, requestPath, params):
    str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))

    source = "%s%s%s?%s" % (
        requestMethod.upper(),
        requestHost,
        requestPath,
        str_params
    )
    return source


def sign(requestMethod, requestHost, requestPath, params, secretKey):
    source = makePlainText(requestMethod, requestHost, requestPath, params)
    hashed = hmac.new(secretKey, source, hashlib.sha1)
    return binascii.b2a_base64(hashed.digest())[:-1]


def getSubDomains(rootDomain, secret_id, secret_key, log_instance):
    """
    获取所有子域名
    """
    # 请求参数
    base_arg = {
        "Timestamp": int(time.time()),
        "Nonce": int(random.random()),
        "SecretId": secret_id,
    }
    base_arg.update({
        "domain": rootDomain,
        "Action": "RecordList"
    })
    params = base_arg

    sing_text = sign(requestMethod, requestHost, requestPath, params, secret_key)

    params["Signature"] = sing_text

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    httpsConn = None
    try:
        httpsConn = httplib.HTTPSConnection(host=requestHost, port=443)
        if requestMethod == "GET":
            params["Signature"] = urllib.quote(sing_text)

            str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))
            url = "https://%s%s?%s" % (requestHost, requestPath, str_params)
            httpsConn.request("GET", url)
        elif requestMethod == "POST":
            params = urllib.urlencode(params)
            httpsConn.request("POST", requestPath, params, headers)

        response = httpsConn.getresponse()
        data = response.read()
        # print data
        jsonRet = json.loads(data)
        return jsonRet

    except Exception, e:
        log_instance.error(u"{}".format(e))
    finally:
        if httpsConn:
            httpsConn.close()


def update_record(rootdomain, recordid, host, recordtype, value, secret_id, secret_key, log_instance):
    """
    更新DNS解析记录
    """
    # 请求参数
    base_arg = {
        "Timestamp": int(time.time()),
        "Nonce": int(random.random()),
        "SecretId": secret_id,
    }
    base_arg.update({
        "domain": rootdomain,
        "recordId": recordid,
        "subDomain": host,
        "recordType": recordtype,
        "recordLine": "默认",
        "value": value,
        "Action": "RecordModify"
    })
    params = base_arg

    sing_text = sign(requestMethod, requestHost, requestPath, params, secret_key)

    params["Signature"] = sing_text

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    httpsConn = None
    try:
        httpsConn = httplib.HTTPSConnection(host=requestHost, port=443)
        if requestMethod == "GET":
            params["Signature"] = urllib.quote(sing_text)

            str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))
            url = "https://%s%s?%s" % (requestHost, requestPath, str_params)
            httpsConn.request("GET", url)
        elif requestMethod == "POST":
            params = urllib.urlencode(params)
            httpsConn.request("POST", requestPath, params, headers)

        response = httpsConn.getresponse()
        data = response.read()
        # print data
        jsonRet = json.loads(data)
        return jsonRet

    except Exception, e:
        log_instance.error(u"{}".format(e))
    finally:
        if httpsConn:
            httpsConn.close()


if __name__ == "__main__":
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
        log_file = "%s/dns.log" % os.path.abspath(os.path.dirname(__file__))
    else:
        log_file = "%s/{}" % os.path.abspath(os.path.dirname(__file__))

    log_instance = appLog("ORAY_INSTEAD", log_file)

    dst_hosts = [HOST]
    wait_interval = 10
    # 初始化检测 当前出口IP与云端IP异同
    now_ip = get_local_ip(log_instance, RECEIVERS=RECEIVERS)
    if now_ip["status"] == "ok":
        now_nsip = ""
        for record in getSubDomains(ROOT_DOMAIN, SecretID, SecretKEY, log_instance)["data"]["records"]:
            for host in dst_hosts:
                if host == record["name"]:
                    now_nsip = record["value"]
                    if now_ip["ip"] != now_nsip:
                        res = update_record(ROOT_DOMAIN, record["id"], host, "A", now_ip["ip"], SecretID, SecretKEY,
                                            log_instance)
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
                allSubDomains = getSubDomains(ROOT_DOMAIN, SecretID, SecretKEY, log_file)
                for record in allSubDomains["data"]["records"]:
                    for host in dst_hosts:
                        if host == record["name"]:
                            res = update_record(ROOT_DOMAIN, record["id"], host, "A", new_ip["ip"], SecretID, SecretKEY,
                                                log_file)
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
