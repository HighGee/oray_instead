# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-03-02 22:43

import os


class own_cfg:
    log_path = "{}/log/".format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    log_file = log_path + "dns.log"
