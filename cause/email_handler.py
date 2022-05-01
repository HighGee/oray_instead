# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2019-02-28 22:24
import re
import smtplib
import requests
from email.mime.text import MIMEText
from email.header import Header
from cause.log_handler import own_log
from cause.config import own_cfg

email_logger = own_log('EMAIL')


class IsMail():
    """
    判断是否为邮箱地址
    """

    def __init__(self):
        self.p = re.compile(r"[^\._][\w\._-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$")

    def ismail(self, str):
        res = self.p.match(str)
        if res:
            return True
        else:
            return False


def send_errmsg(receiver, title=None, content=None):
    """
    邮件通知模块
    """

    ipipNetUrl = "http://myip.ipip.net"
    is_email = IsMail()
    if is_email.ismail(receiver[0]):
        if title is None:
            title = u"[故障]出口IP获取异常"
        if content is None:
            try:
                content = requests.get(ipipNetUrl).content
            except Exception:
                content = u"外网断开，无法获取出口IP"
        msg = MIMEText(content, "html", _charset="utf-8")
        me = "admin@haiji.io"
        msg["Subject"] = Header(title, charset="utf-8")
        msg["From"] = me
        msg["To"] = ";".join(receiver)

        try:
            if own_cfg.smtp_ssl:
                s = smtplib.SMTP_SSL(host=own_cfg.smtp_host,
                                     port=own_cfg.smtp_port)
            else:
                s = smtplib.SMTP(host=own_cfg.smtp_host,
                                 port=own_cfg.smtp_port)
            s.set_debuglevel(1)
            s.login(own_cfg.smtp_user, own_cfg.smtp_pass)
            s.sendmail(me, receiver, msg.as_string())
            s.quit()
        except Exception as e:
            email_logger.error(u"邮件通知失败，目标邮箱：%s %s" % (";".join(receiver), e))
    else:
        email_logger.error(u"邮件通知失败，目标邮箱：%s" % ";".join(receiver))


def mail_mass(title=None, content=None):
    receivers = own_cfg.RECEIVERS
    if receivers:
        for email in receivers:
            send_errmsg([email], title=title, content=content)
