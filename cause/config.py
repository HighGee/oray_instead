# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-03-02 22:43

import os


class own_cfg:
    log_path = "{}/log/".format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    log_file = log_path + "dns.log"

    smtp_ssl = True
    smtp_host = 'smtp.example.com'
    smtp_port = 465
    smtp_user = 'username'
    smtp_pass = 'password'
