#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import urllib
import os
import httplib
import binascii
import hashlib
import requests
import hmac
import time
import random
import commands
import json
import re
from pyquery import PyQuery
import argparse

# 腾讯云API TOKEN信息
requestMethod = 'POST'
requestHost = 'cns.api.qcloud.com'
requestPath = '/v2/index.php'


def updateLog(log, logfile):
    log_record = "%s %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), log)
    commands.getoutput("echo %s >> %s" % (log_record, logfile))


def getOwnIp(logfile):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0"}
    try:
        ipQueryRes = requests.get("http://www.ipip.net", headers=headers).content
        ip_content = PyQuery(ipQueryRes)('.ip_text').text()
        ipPattern = r'\d+.\d+.\d+.\d+'
        rep = re.compile(ipPattern)
        result = {"status":"ok","ip":rep.findall(ip_content)[0]}
    except:
        updateLog('当前网络异常，无法获取出口IP',logfile)
        result = {"status":"wrong"}

    return result


def makePlainText(requestMethod, requestHost, requestPath, params):
    str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))

    source = '%s%s%s?%s' % (
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


def getSubDomains(rootDomain, secret_id, secret_key, logfile):
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

    params['Signature'] = signText

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    httpsConn = None
    try:
        httpsConn = httplib.HTTPSConnection(host=requestHost, port=443)
        if requestMethod == "GET":
            params['Signature'] = urllib.quote(signText)

            str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))
            url = 'https://%s%s?%s' % (requestHost, requestPath, str_params)
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
        updateLog(e, logfile)
    finally:
        if httpsConn:
            httpsConn.close()


def updateRecord(rootdomain, recordid, host, recordtype, value, secret_id, secret_key, logfile):
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

    params['Signature'] = signText

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    httpsConn = None
    try:
        httpsConn = httplib.HTTPSConnection(host=requestHost, port=443)
        if requestMethod == "GET":
            params['Signature'] = urllib.quote(signText)

            str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))
            url = 'https://%s%s?%s' % (requestHost, requestPath, str_params)
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
        updateLog(e, logfile)
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
    parsers.add_argument("--logfile", type=str, help="日志文件的绝对路径，默认脚本所在路径下dns.log")
    FLAGS, unparsed = parsers.parse_known_args()

    SecretID = FLAGS.secret_id
    SecretKEY = FLAGS.secret_key
    ROOT_DOMAIN = FLAGS.root_domain
    HOST = FLAGS.host
    LOGFILE = FLAGS.logfile

    if LOGFILE is None:
        LOGFILE = '%s/dns.log' % os.path.abspath(os.path.dirname(__file__))

    dst_hosts = [HOST]
    # 初始化检测 当前出口IP与云端IP异同
    now_ip = getOwnIp(LOGFILE)
    if now_ip["status"] == "ok":
        now_nsip = ''
        for record in getSubDomains(ROOT_DOMAIN, SecretID, SecretKEY,LOGFILE)["data"]["records"]:
            for host in dst_hosts:
                if host == record["name"]:
                    now_nsip = record["value"]
                    if now_ip["ip"] != now_nsip:
                        res = updateRecord(ROOT_DOMAIN, record["id"], host, "A", now_ip["ip"], SecretID, SecretKEY, LOGFILE)
                        if res["codeDesc"] == "Success":
                            updateLog("初始化 解析更新成功 新IP为:%s" % (now_ip["ip"]), LOGFILE)
                            time.sleep(300)
                    else:
                        updateLog("初始化成功 当前IP为:%s" % (now_ip["ip"]), LOGFILE)
                        time.sleep(300)
    else:
        time.sleep(10)
    # 监控变化
    while True:
        new_ip = getOwnIp(LOGFILE)
        if new_ip["status"] == "ok":
            if now_ip["status"] == "ok" and new_ip["ip"] == now_ip["ip"]:
                updateLog("解析未更新 当前IP为:%s" % (new_ip["ip"]), LOGFILE)
                time.sleep(int(random.random() * 500))
                pass
            else:
                allSubDomains = getSubDomains(ROOT_DOMAIN, SecretID, SecretKEY, LOGFILE)
                for record in allSubDomains["data"]["records"]:
                    for host in dst_hosts:
                        if host == record["name"]:
                            res = updateRecord(ROOT_DOMAIN, record["id"], host, "A", new_ip["ip"], SecretID, SecretKEY, LOGFILE)
                            if res["codeDesc"] == "Success":
                                now_ip["ip"] = new_ip["ip"]
                                now_ip["status"] = "ok"
                                updateLog("解析更新成功 新IP为:%s" % (new_ip["ip"]), LOGFILE)

        else:
            time.sleep(10)
