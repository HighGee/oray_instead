# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:27
import logging
import sentry_sdk
from logging.handlers import TimedRotatingFileHandler
from cause.config import own_cfg
from sentry_sdk.integrations.logging import LoggingIntegration


# All of this is already happening by default!
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)
sentry_sdk.init(
    own_cfg.SENTRY_DSN,
    integrations=[sentry_logging]
)

# logging.debug("I am ignored")
# logging.info("I am a breadcrumb")
# logging.error("I am an event", extra=dict(bar=43))
# logging.error("An exception happened", exc_info=True)


def own_log(app_name):
    """
    日志模块
    """
    log_instance = logging.getLogger(app_name)
    log_instance.setLevel(logging.DEBUG)

    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(filename)s:%(lineno)d %(levelname)s %(message)s")
    formatter.datefmt = "%Y-%m-%d %H:%M:%S"

    file_handler = TimedRotatingFileHandler(
        own_cfg.log_file, when='D', backupCount=30)
    file_handler.setFormatter(formatter)
    log_instance.addHandler(file_handler)

    return log_instance
