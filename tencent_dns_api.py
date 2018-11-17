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
own_srv_url = "https://haiji.io/get_way_out.php"
ipipnet_url = "http://myip.ipip.net"

"""
判断是否为邮箱地址
"""


class IsMail():
    def __init__(self):
        self.p = re.compile(r"[^\._][\w\._-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$")

    def ismail(self, str):
        res = self.p.match(str)
        if res:
            return True
        else:
            return False


"""
日志模块
"""


def appLog(appname, LOGFILE):
    logger = logging.getLogger(appname)
    logger.setLevel(logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter("%(asctime)s %(name)s %(filename)s %(levelname)s %(message)s")
    formatter.datefmt = "%Y-%m-%d %H:%M:%S"

    file_handler = logging.FileHandler(LOGFILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


"""
邮件通知模块
"""


def send_errmsg(receiver, title=None, content=None):
    is_email = IsMail()
    if is_email.ismail(receiver[0]):
        if title is None:
            title = u"OI出口获取异常通知"
        if content is None:
            content = requests.get(ipipnet_url).content
        msg = MIMEText(content, "html", _charset="utf-8")
        me = "OI@highgee.com"
        msg["Subject"] = Header(title, charset="utf-8")
        msg["From"] = me
        msg["To"] = ";".join(receiver)

        s = smtplib.SMTP("localhost")
        s.sendmail(me, receiver, msg.as_string())
        s.quit()
    else:
        logger.error(u"邮件通知失败，目标邮箱：%s" % ";".join(receiver))


def mail_mass(RECEIVERS, title=None, content=None):
    if RECEIVERS is not None:
        if ";" in RECEIVERS:
            for email in RECEIVERS.split(";"):
                send_errmsg([email], title=title, content=content)
        else:
            send_errmsg([RECEIVERS], title=title, content=content)


"""
出口IP获取模块
"""


def getOwnIp(logger, RECEIVERS=None):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0"}
    try:
        rep = requests.get(own_srv_url, headers=headers)
        if rep.status_code != 200:
            logger.error(u"站点访问异常，无法获取出口IP，状态码为 {}".format(rep.status_code))
            result = {"status": "wrong", "msg": "http_status"}
            ban_codes = [403, 521, 555]
            err_codes = [404, 502, 504]
            if rep.status_code in ban_codes:
                ban_title = u"请求被拦截，状态码为{}".format(rep.status_code)
            elif rep.status_code in err_codes:
                ban_title = u"源站或异常，状态码为{}".format(rep.status_code)
            else:
                ban_title = u"未收录异常，状态码为{}".format(rep.status_code)

            mail_mass(RECEIVERS, ban_title)
        else:
            my_ip = json.loads(rep.content)["client_ip"]
            result = {"status": "ok", "ip": my_ip}
    except Exception, e:
        logger.error(u"当前网络异常，无法获取出口IP，{}".format(e))
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


def getSubDomains(rootDomain, secret_id, secret_key, logger):
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

    signText = sign(requestMethod, requestHost, requestPath, params, secret_key)

    params["Signature"] = signText

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    httpsConn = None
    try:
        httpsConn = httplib.HTTPSConnection(host=requestHost, port=443)
        if requestMethod == "GET":
            params["Signature"] = urllib.quote(signText)

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
        logger.error(u"{}".format(e))
    finally:
        if httpsConn:
            httpsConn.close()


"""
更新DNS记录
"""


def updateRecord(rootdomain, recordid, host, recordtype, value, secret_id, secret_key, logger):
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

    signText = sign(requestMethod, requestHost, requestPath, params, secret_key)

    params["Signature"] = signText

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    httpsConn = None
    try:
        httpsConn = httplib.HTTPSConnection(host=requestHost, port=443)
        if requestMethod == "GET":
            params["Signature"] = urllib.quote(signText)

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
        logger.error(u"{}".format(e))
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
    parsers.add_argument("--logfile", type=str, help="日志文件的绝对路径，默认脚本所在路径下dns.log")
    FLAGS, unparsed = parsers.parse_known_args()

    SecretID = FLAGS.secret_id
    SecretKEY = FLAGS.secret_key
    ROOT_DOMAIN = FLAGS.root_domain
    RECEIVERS = FLAGS.receivers
    HOST = FLAGS.host
    LOGFILE = FLAGS.logfile

    if LOGFILE is None:
        LOGFILE = "%s/dns.log" % os.path.abspath(os.path.dirname(__file__))

    logger = appLog("ORAY_INSTEAD", LOGFILE)

    dst_hosts = [HOST]
    wait_interval = 10
    # 初始化检测 当前出口IP与云端IP异同
    now_ip = getOwnIp(logger, RECEIVERS=RECEIVERS)
    if now_ip["status"] == "ok":
        now_nsip = ""
        for record in getSubDomains(ROOT_DOMAIN, SecretID, SecretKEY, logger)["data"]["records"]:
            for host in dst_hosts:
                if host == record["name"]:
                    now_nsip = record["value"]
                    if now_ip["ip"] != now_nsip:
                        res = updateRecord(ROOT_DOMAIN, record["id"], host, "A", now_ip["ip"], SecretID, SecretKEY,
                                           logger)
                        if res["codeDesc"] == "Success":
                            logger.info("初始化 解析更新成功 新IP为:{}".format(now_ip["ip"]))
                            time.sleep(wait_interval)
                    else:
                        logger.info("初始化成功 当前IP为:{}".format(now_ip["ip"]))
                        time.sleep(wait_interval)
    else:
        if now_ip["msg"] == "exception":
            time.sleep(wait_interval)
        else:
            time.sleep(wait_interval)

    # 监控变化
    while True:
        new_ip = getOwnIp(logger, RECEIVERS=RECEIVERS)
        if new_ip["status"] == "ok":
            if now_ip["status"] == "ok" and new_ip["ip"] == now_ip["ip"]:
                time.sleep(wait_interval)
            else:
                allSubDomains = getSubDomains(ROOT_DOMAIN, SecretID, SecretKEY, LOGFILE)
                for record in allSubDomains["data"]["records"]:
                    for host in dst_hosts:
                        if host == record["name"]:
                            res = updateRecord(ROOT_DOMAIN, record["id"], host, "A", new_ip["ip"], SecretID, SecretKEY,
                                               LOGFILE)
                            if res["codeDesc"] == "Success":
                                now_ip["ip"] = new_ip["ip"]
                                now_ip["status"] = "ok"
                                logger.info("解析更新成功 新IP为:{}".format(new_ip["ip"]))
                time.sleep(wait_interval)

        else:
            if new_ip["status"] == "wrong" and new_ip["msg"] == "http_status":
                time.sleep(wait_interval * 60)
            else:
                time.sleep(wait_interval)
