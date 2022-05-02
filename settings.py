# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-03-02 22:43
import yaml
from os import path as osp


_dir = osp.dirname(osp.abspath(__file__))
LOG_FILE = osp.join(_dir, 'log/dns.log')

# 邮件
MAIL_FROM = 'admin@example.com'
SMTP_CONF = {
    "is_ssl": True,
    "host": 'smtp.example.com',
    "port": 465,
    "user": 'username',
    "pass": 'password',
}

# 更新频率
INTERVAL = 1

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
RECEIVERS = ['mail1@example.com', 'mail2@example.com']
SENTRY_DSN = ''

LOG_LEVEL = 'WARNING'

HTTP_BAN_CODES = [403, 521, 555]
HTTP_ERR_CODES = [404, 502, 504]

IPIPNET_URL = "http://myip.ipip.net"

yaml_config = yaml.load(open(
    osp.join(_dir, 'settings.yaml'), 'r', encoding='utf-8'),
    Loader=yaml.FullLoader)
for k, v in yaml_config.items():
    locals()[k] = v
