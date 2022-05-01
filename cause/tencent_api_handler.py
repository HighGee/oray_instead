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
import traceback
from cause.config import own_cfg
from cause.log_handler import own_log
from urllib.parse import urlencode, quote

tencent_logger = own_log("TENCENT_API")
TENCENT_PATH = own_cfg.REQUEST["path"]
TENCENT_HOST = own_cfg.REQUEST["host"]
TENCENT_METH = own_cfg.REQUEST["method"]
SECRET_ID = own_cfg.SECRET_ID
SECRET_KEY = own_cfg.SECRET_KEY


def make_plain_text(params):
    sorted_keys = sorted(params.keys())
    url_args = [k + "=" + str(params[k]) for k in sorted_keys]
    str_params = "&".join(url_args)

    source = "%s%s%s?%s" % (
        TENCENT_METH.upper(),
        TENCENT_HOST,
        TENCENT_PATH,
        str_params
    )
    return source


def sign(params):
    source = make_plain_text(params)
    hashed = hmac.new(SECRET_KEY.encode(), source.encode(), hashlib.sha1)
    return binascii.b2a_base64(hashed.digest())[:-1]


def getSubDomains(rootDomain):
    """
    获取所有子域名
    """
    # 请求参数
    base_arg = {
        "Timestamp": int(time.time()),
        "Nonce": int(random.random()),
        "SecretId": SECRET_ID,
    }
    base_arg.update({
        "domain": rootDomain,
        "Action": "RecordList"
    })
    params = base_arg

    sing_text = sign(params)

    params["Signature"] = sing_text

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    https_conn = None
    try:
        https_conn = http.client.HTTPSConnection(host=TENCENT_HOST, port=443)
        if TENCENT_METH == "GET":
            params["Signature"] = quote(sing_text)
            str_params = "&".join(
                k + "=" + str(params[k]) for k in sorted(params.keys()))
            url = "https://%s%s?%s" % (TENCENT_HOST, TENCENT_PATH, str_params)
            https_conn.request("GET", url)
        elif TENCENT_METH == "POST":
            params = urlencode(params)
            https_conn.request("POST", TENCENT_PATH, params, headers)

        response = https_conn.getresponse()
        data = response.read()
        # print data
        jsonRet = json.loads(data)
        return jsonRet

    except Exception:
        tencent_logger.error(traceback.format_exc())
    finally:
        if https_conn:
            https_conn.close()


def update_record(rootdomain, recordid, host, recordtype, value):
    """
    更新DNS解析记录
    """
    # 请求参数
    base_arg = {
        "Timestamp": int(time.time()),
        "Nonce": int(random.random()),
        "SecretId": SECRET_ID,
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

    sing_text = sign(params)

    params["Signature"] = sing_text

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    # 发送请求
    https_conn = None
    try:
        https_conn = http.client.HTTPSConnection(host=TENCENT_HOST, port=443)
        if TENCENT_METH == "GET":
            params["Signature"] = quote(sing_text)
            str_params = "&".join(
                k + "=" + str(params[k]) for k in sorted(params.keys()))
            url = "https://%s%s?%s" % (TENCENT_HOST, TENCENT_PATH, str_params)
            https_conn.request("GET", url)
        elif TENCENT_METH == "POST":
            params = urlencode(params)
            https_conn.request("POST", TENCENT_PATH, params, headers)

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
