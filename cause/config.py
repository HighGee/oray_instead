# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-03-02 22:43

import os
from os import path as osp
import yaml

_dir = osp.dirname(osp.abspath(__file__))


class own_cfg:
    log_path = "{}/log/".format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    log_file = log_path + "dns.log"

    SMTP_CONF = {
        "is_ssl": True,
        "host":'smtp.example.com',
        "port": 465,
        "user": 'username',
        "pass":'password',
    }
    # 腾讯
    REQUEST = {
        "method": "POST",
        "host": "cns.api.qcloud.com",
        "path": "/v2/index.php"
    }
    SECRET_ID = ''
    SECRET_KEY = ''
    DNS_DOMAIN = 'example.com'
    DNS_HOST = 'test'

    # 告警对象
    RECEIVERS = ['mail1@example.com','mail2@example.com']
    SENTRY_DSN = ''

    LOG_LEVEL = 'WARNING'

    yaml_config = yaml.load(open(osp.join(_dir,'config.yaml'), 'r', encoding='utf-8'), Loader=yaml.FullLoader)
    for k, v in yaml_config.items():
        locals()[k] = v