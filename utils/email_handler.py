# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:24
import re
import smtplib
import requests
from email.mime.text import MIMEText
from email.header import Header
from utils.log_handler import own_log
from settings import (
    RECEIVERS,
    SMTP_CONF,
    IPIPNET_URL,
    MAIL_FROM
)


LOGGER = own_log('EMAIL')
SMTP_SSL = SMTP_CONF.get('is_ssl', True)
SMTP_HOST = SMTP_CONF.get('host', '')
SMTP_PORT = SMTP_CONF.get('port', 465)
SMTP_USER = SMTP_CONF.get('user', '')
SMTP_PASS = SMTP_CONF.get('pass', '')
EMAIL_REG = re.compile(r"[^\._][\w\._-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$")


def isEmail(email_str):
    return True if EMAIL_REG.match(email_str) else False


def send_errmsg(receiver, title=None, content=None):
    """
    邮件通知模块
    """

    if not isEmail(receiver[0]):
        LOGGER.error(u"邮件通知失败，目标邮箱：%s" % ";".join(receiver))
        return

    if not title:
        title = u"[故障]出口IP获取异常"
    if not content:
        try:
            content = requests.get(IPIPNET_URL).content
        except Exception:
            content = u"外网断开，无法获取出口IP"
    msg = MIMEText(content, "html", _charset="utf-8")
    msg["Subject"] = Header(title, charset="utf-8")
    msg["From"] = MAIL_FROM
    msg["To"] = ";".join(receiver)

    try:
        if SMTP_SSL:
            s = smtplib.SMTP_SSL(host=SMTP_HOST,
                                 port=SMTP_PORT)
        else:
            s = smtplib.SMTP(host=SMTP_HOST,
                             port=SMTP_PORT)
        s.set_debuglevel(1)
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(MAIL_FROM, receiver, msg.as_string())
        s.quit()
    except Exception as e:
        LOGGER.error(u"邮件通知失败，目标邮箱：%s %s" % (";".join(receiver), e))


def mail_mass(title=None, content=None):
    if RECEIVERS:
        for receiver in RECEIVERS:
            send_errmsg([receiver], title=title, content=content)
