# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:27
import logging
from logging.handlers import TimedRotatingFileHandler


def own_log(app_name, log_file):
    """
    日志模块
    """
    log_instance = logging.getLogger(app_name)
    log_instance.setLevel(logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter("%(asctime)s %(name)s %(filename)s::%(lineno)d %(levelname)s %(message)s")
    formatter.datefmt = "%Y-%m-%d %H:%M:%S"

    file_handler = TimedRotatingFileHandler(log_file, when='D', backupCount=30)
    file_handler.setFormatter(formatter)
    log_instance.addHandler(file_handler)

    return log_instance
