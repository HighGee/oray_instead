# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:28
import hashlib
import binascii
import hmac
import http.client
import time
import random
import json
from cause.config import own_cfg
from cause.log_handler import own_log
from urllib.parse import urlencode, quote

tencent_logger = own_log("TENCENT_API", own_cfg.log_file)


def make_plain_text(request_method, requet_host, request_path, params):
    str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))

    source = "%s%s%s?%s" % (
        request_method.upper(),
        requet_host,
        request_path,
        str_params
    )
    return source


def sign(request_method, requet_host, request_path, params, secretKey):
    source = make_plain_text(request_method, requet_host, request_path, params)
    hashed = hmac.new(secretKey.encode(), source.encode(), hashlib.sha1)
    return binascii.b2a_base64(hashed.digest())[:-1]


def getSubDomains(rootDomain, secret_id, secret_key, request_method, requet_host, request_path):
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

    sing_text = sign(request_method, requet_host, request_path, params, secret_key)

    params["Signature"] = sing_text

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    https_conn = None
    try:
        https_conn = http.client.HTTPSConnection(host=requet_host, port=443)
        if request_method == "GET":
            params["Signature"] = quote(sing_text)

            str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))
            url = "https://%s%s?%s" % (requet_host, request_path, str_params)
            https_conn.request("GET", url)
        elif request_method == "POST":
            params = urlencode(params)
            https_conn.request("POST", request_path, params, headers)

        response = https_conn.getresponse()
        data = response.read()
        # print data
        jsonRet = json.loads(data)
        return jsonRet

    except Exception as  e:
        tencent_logger.error(u"{}".format(e))
    finally:
        if https_conn:
            https_conn.close()


def update_record(rootdomain, recordid, host, recordtype, value, secret_id, secret_key, request_method,
                  requet_host, request_path):
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

    sing_text = sign(request_method, requet_host, request_path, params, secret_key)

    params["Signature"] = sing_text

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    https_conn = None
    try:
        https_conn = http.client.HTTPSConnection(host=requet_host, port=443)
        if request_method == "GET":
            params["Signature"] = quote(sing_text)

            str_params = "&".join(k + "=" + str(params[k]) for k in sorted(params.keys()))
            url = "https://%s%s?%s" % (requet_host, request_path, str_params)
            https_conn.request("GET", url)
        elif request_method == "POST":
            params = urlencode(params)
            https_conn.request("POST", request_path, params, headers)

        response = https_conn.getresponse()
        data = response.read()
        # print data
        jsonRet = json.loads(data)
        return jsonRet

    except Exception as e:
        tencent_logger.error(u"{}".format(e))
    finally:
        if https_conn:
            https_conn.close()
