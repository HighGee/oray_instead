# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:27
import logging
import sentry_sdk
from logging.handlers import TimedRotatingFileHandler
from sentry_sdk.integrations.logging import LoggingIntegration

from settings import (
    LOG_FILE,
    SENTRY_DSN
)

sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)
sentry_sdk.init(
    SENTRY_DSN,
    integrations=[sentry_logging]
)


def own_log(app_name):
    """
    日志模块
    """
    log_instance = logging.getLogger(app_name)
    log_instance.setLevel(logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter('[%(asctime)s]%(filename)s-%(process)d-%(thread)d-%(lineno)d-%(levelname)8s-"%(message)s"', '%Y-%m-%d %a %H:%M:%S')  # noqa

    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when='D', backupCount=30)
    file_handler.setFormatter(formatter)
    log_instance.addHandler(file_handler)

    return log_instance
