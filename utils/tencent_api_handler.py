# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:28
import hmac
import time
import json
import random
import hashlib
import binascii
import traceback
import http.client
from utils.log_handler import own_log
from urllib.parse import urlencode, quote

from settings import (
    REQUEST,
    SECRET_ID,
    SECRET_KEY
)

LOGGER = own_log("TENCENT_API")


class TencentCloudAPI(object):
    def __init__(self) -> None:
        self.TENCENT_PATH = REQUEST.get("path", '')
        self.TENCENT_HOST = REQUEST.get("host", '')
        self.TENCENT_METH = REQUEST.get("method", '')

    def __str_params(self, params):
        sorted_keys = sorted(params.keys())
        url_args = [k + "=" + str(params[k]) for k in sorted_keys]
        str_params = "&".join(url_args)
        return str_params

    def make_plain_text(self, params):
        source = "%s%s%s?%s" % (
            self.TENCENT_METH.upper(),
            self.TENCENT_HOST,
            self.TENCENT_PATH,
            self.__str_params(params)
        )
        return source

    def sign(self, params):
        source = self.make_plain_text(params)
        hashed = hmac.new(SECRET_KEY.encode(), source.encode(), hashlib.sha1)
        return binascii.b2a_base64(hashed.digest())[:-1]

    def __get_http_conn(self, params, sign_text):
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        http_conn = http.client.HTTPSConnection(
            host=self.TENCENT_HOST, port=443)
        if self.TENCENT_METH == "GET":
            params["Signature"] = quote(sign_text)
            url = "https://%s%s?%s" % (self.TENCENT_HOST,
                                       self.TENCENT_PATH,
                                       self.__str_params(params))
            http_conn.request("GET", url)
        elif self.TENCENT_METH == "POST":
            params = urlencode(params)
            http_conn.request("POST", self.TENCENT_PATH, params, headers)
        return http_conn

    def getSubDomains(self, rootDomain):
        """
        获取所有子域名
        """
        # 请求参数
        params = {
            "Timestamp": int(time.time()),
            "Nonce": int(random.random()),
            "SecretId": SECRET_ID,
            "domain": rootDomain,
            "Action": "RecordList"
        }

        sign_text = self.sign(params)
        params["Signature"] = sign_text
        http_conn = None
        try:
            http_conn = self.__get_http_conn(params, sign_text)
            response = http_conn.getresponse()
            data = response.read()
            return json.loads(data)
        except Exception:
            LOGGER.error(traceback.format_exc())
        finally:
            if http_conn:
                http_conn.close()

    def updateRecord(self, rootdomain, recordid, host, recordtype, value):
        """
        更新DNS解析记录
        """
        # 请求参数
        params = {
            "Timestamp": int(time.time()),
            "Nonce": int(random.random()),
            "SecretId": SECRET_ID,
            "domain": rootdomain,
            "recordId": recordid,
            "subDomain": host,
            "recordType": recordtype,
            "recordLine": "默认",
            "value": value,
            "Action": "RecordModify"
        }

        sign_text = self.sign(params)
        params["Signature"] = sign_text
        http_conn = None
        try:
            http_conn = self.__get_http_conn(params, sign_text)
            response = http_conn.getresponse()
            data = response.read()
            return json.loads(data)
        except Exception:
            LOGGER.error(traceback.format_exc())
        finally:
            if http_conn:
                http_conn.close()
